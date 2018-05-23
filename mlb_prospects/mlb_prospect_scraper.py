import requests
import urllib
import csv
import os
import sys
import datetime
import codecs
import argparse
from time import time, sleep


from py_data_getter import data_getter
from py_db import db


db = db("mlb_prospects")
getter = data_getter()

sleep_time = 0

base_url = "http://m.mlb.com/gen/players/prospects/%s/playerProspects.json"
player_base_url = "http://m.mlb.com/gen/players/prospects/%s/%s.json"
player2_base_url = "http://mlb.com/lookup/json/named.player_info.bam?sport_code='mlb'&player_id=%s"

def initiate(end_year, scrape_length):
    start_time = time()

    if scrape_length == "All":
        for year in range (2013, end_year+1):
            process(year)
    else:
        year = end_year
        process(year)


    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nmlb_prospect_scraper.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def process(year):
    url = base_url % year
    print(url)
    json = getter.get_url_data(url, "json")
    prospect_lists = json["prospect_players"]
    scrape_prospects(year, prospect_lists)


def scrape_prospects(year, prospect_lists):

    list_cnt = 0
    for list_type in (prospect_lists):
        entries = []
        if list_type not in ("rule5", "prospects", "pdp", "rhp", "lhp", "c", "1b", "2b", "3b", "ss", "of"):
        # if list_type in ("draft","int"):
            list_cnt += 1
            ind_list = prospect_lists[list_type]
            
            i = 0
            for player in ind_list:
                entry = {}
                i += 1
                sleep(sleep_time)
                mlb_id = player["player_id"]
                player_url = player_base_url % (year, mlb_id)
                
                print list_cnt, year, list_type, "\t", str(mlb_id)
                print "\t\t", str(player_url)

                sleep(sleep_time)
                player_json = getter.get_url_data(player_url, "json")

                try:
                    player_info = player_json["prospect_player"]
                except TypeError:
                    print "\n\n**ERROR TAG** TYPE_ERROR", str(year), str(mlb_id), "\n\n"
                    continue

                fname = player_info["player_first_name"]
                lname = player_info["player_last_name"]
                fname, lname = adjust_names(mlb_id, fname, lname)

                position = player_info["positions"]
                position = adjust_positions(mlb_id, position)

                entry["year"] = year
                entry["rank"] = i
                entry["mlb_id"] = mlb_id
                entry["fname"] = fname
                entry["lname"] = lname
                entry["position"] = position


                if list_type in ("int","draft"):
                    bats = player_info["bats"]
                    throws = player_info["thrw"]
                    try:
                        height = player_info["height"].replace("\"","").split("\"")
                        height = int(height[0])*12+int(height[1])
                    except (IndexError, ValueError, AttributeError):
                        height = None
                    weight = player_info["weight"]
                    try:
                        dob = player_info["birthdate"]
                        byear = dob.split("/")[2]
                        bmonth = dob.split("/")[0]
                        bday = dob.split("/")[1]
                    except IndexError:
                        print '\n\nNO BIRTHDAY', fname, lname, mlb_id, "\n\n"
                        continue

                    byear, bmonth, bday = adjust_birthdays(mlb_id, byear, bmonth, bday)

                    prospect_id = add_prospect(mlb_id, fname, lname, byear, bmonth, bday, p_type=list_type)

                else:
                    info_url = player2_base_url % mlb_id
                    print "\t\t", info_url

                    sleep(sleep_time)
                    info_json = getter.get_url_data(info_url, "json", json_unicode_convert=True)
                    try:
                        info_info = info_json["player_info"]["queryResults"]["row"]
                    except TypeError:
                        print "\n\n**ERROR TAG** MLB_ERROR", str(year), str(mlb_id), str(fname), str(lname), "\n\n"
                        continue
                        
                    dob = info_info["birth_date"]
                    byear = dob.split("-")[0]
                    bmonth = dob.split("-")[1]
                    bday = dob.split("-")[2].split("T")[0]

                    prospect_id = add_prospect(mlb_id, fname, lname, byear, bmonth, bday, p_type="professional")

                    try:
                        bats = info_info["bats"]
                        throws = info_info["throws"]
                        height = int(info_info["height_feet"])*12+int(info_info["height_inches"])
                        weight = int(info_info["weight"])                  
                    except UnicodeDecodeError:
                        bats, throws, height, weight = (None, None, None, None)
                    except ValueError:
                        print "\n\n**ERROR TAG** MLB_ERROR", str(year), str(mlb_id), str(fname), str(lname), "\n\n"
                        continue

                entry["prospect_id"] = prospect_id
                entry["bats"] = bats
                entry["throws"] = throws
                entry["height"] = height
                entry["weight"] = weight
                entry["birth_year"] = byear
                entry["birth_month"] = bmonth
                entry["birth_day"] = bday

                entry["team"] = player["team_file_code"]
                drafted = player_info["drafted"]                

                if list_type == "int":
                    drafted = None
                    try:
                        sign_text = player_info["signed"]
                        sign_value = sign_text.split(" - ")[1]
                        signed = sign_value
                    except IndexError:
                        signed = ""
                    try:
                        signed = int(signed.replace("$","").replace(",",""))
                    except ValueError:
                        signed = None

                    schoolcity = player_info["school"]
                    gradecountry = player_info["year"]
                    commit = None

                elif list_type == "draft":
                    try:
                        signed = player_info["preseason20"].replace(" ","").replace(",","").replace("$","").split("-")[1]
                    except (KeyError, IndexError):
                        signed = player_info["signed"].replace(" ","").replace(",","").replace("$","")
                    try:
                        signed = int(signed)
                    except ValueError:
                        signed = None
                    schoolcity = player_info["school"]
                    gradecountry = player_info["year"]
                    commit = player_info["signed"]
                else:
                    signed = player_info["signed"]
                    schoolcity = None
                    gradecountry = None
                    commit = None

                entry["drafted"] = drafted
                entry["signed"] = signed
                entry["school_city"] = schoolcity
                entry["grade_country"] = gradecountry
                entry["college_commit"] = commit

                if list_type not in ("int", "draft"):
                    eta = player_info["eta"]
                    try:
                        pre_top100 = player_info["preseason100"]
                    except KeyError:
                        pre_top100 = None
                else:
                    pre_top100 = None
                    eta = None

                entry["pre_top100"] = pre_top100
                entry["eta"] = eta


                entry["twitter"] = player_info["twitter"]


                blurb = player_info["content"]["default"].replace("<b>","").replace("</b>","").replace("<br />","").replace("<p>","").replace("</p>","").replace("*","")
                entry["blurb"] = blurb

                try:
                    overall_text = blurb.split("Overall")[1].split('\n')[0].replace(':','').replace(' ','')[:8]
                    if overall_text[0] not in (' ',':','0','1','2','3','4','5','6','7','8','9'):
                        raise IndexError

                    try:
                        text2 = overall_text.split('/')[1]
                    except IndexError:
                        text2 = overall_text.split('/')[-1]

                    overall = int(filter(str.isdigit, text2[:2]))
                except IndexError:
                    overall = 0

                if overall < 20 and overall is not None:
                    overall = overall*10
                entry["FV"] = overall

                entries.append(entry)


        if list_type == "draft":
            table = "mlb_prospects_draft"
        elif list_type == "int":
            table = "mlb_prospects_international"
        else:
            table = "mlb_prospects_professional"

        if entries != []:
            for i in range(0, len(entries), 1000):
                db.insertRowDict(entries[i: i + 1000], table, insertMany=True, replace=True, rid=0,debug=1)
                db.conn.commit()


def add_prospect(site_id, fname, lname, byear, bmonth, bday, p_type):

    check_qry = """SELECT prospect_id
    FROM professional_prospects
    WHERE(
        (mlb_id = "%s" AND mlb_id != 0)
        OR (mlb_draft_id = "%s" AND mlb_draft_id IS NOT NULL)
        OR (mlb_international_id = "%s" AND mlb_international_id IS NOT NULL)
        OR (fg_id = "%s" AND fg_id IS NOT NULL)
    );
    """

    check_query = check_qry % (site_id, site_id, site_id, site_id)
    check_val = db.query(check_query)

    if check_val != ():
        prospect_id = check_val[0][0]
        return prospect_id
    else:
        check_other_qry = """SELECT prospect_id
        FROM professional_prospects 
        WHERE birth_year = %s
        AND birth_month = %s
        AND birth_day = %s
        AND ((mlb_lname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",mlb_lname,"%%")) OR (fg_lname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",fg_lname,"%%")))
        AND ((mlb_fname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",mlb_fname,"%%")) OR (fg_fname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",fg_fname,"%%")))
        ;"""

        check_other_query = check_other_qry % (byear, bmonth, bday, lname, lname, lname, lname, fname, fname, fname, fname)
        check_other_val = db.query(check_other_query)

        if check_other_val != ():
            prospect_id = check_other_val[0][0]

            f_name = "mlb_fname"
            l_name = "mlb_lname"
            if p_type == "professional":
                id_column = "mlb_id"
            elif p_type == "draft":
                id_column = "mlb_draft_id"
            elif p_type == "int":
                id_column = "mlb_international_id"
            elif p_type == "fg":
                id_column = "fg_id"
                f_name = "fg_fname"
                l_name = "fg_lname"

            for col, val in {f_name:fname, l_name:lname, id_column:site_id}.items():

                if col in ("mlb_id",):
                    set_str = "SET %s = %s" % (col,val)
                    set_str2 = "AND %s = 0" % (col)
                else:
                    set_str = 'SET %s = "%s"' % (col,val)
                    set_str2 = "AND %s IS NULL" % (col)

                update_qry = """UPDATE professional_prospects 
                %s
                WHERE prospect_id = %s 
                %s;"""

                update_query = update_qry % (set_str, prospect_id, set_str2)
                db.query(update_query)
                db.conn.commit()

            return prospect_id

        else:
            entry = {"birth_year":int(byear), "birth_month":int(bmonth), "birth_day":int(bday)}

            if p_type == "fg":
                entry["fg_id"] = site_id
                entry["fg_fname"] = fname
                entry["fg_lname"] = lname
            else:
                entry["mlb_fname"] = fname
                entry["mlb_lname"] = lname
                if p_type == "professional":
                    entry["mlb_id"] = site_id
                elif p_type == "draft":
                    entry["mlb_draft_id"] = site_id
                elif p_type == "int":
                    entry["mlb_international_id"] = site_id

            db.insertRowDict(entry, "professional_prospects", debug=1)
            db.conn.commit()

            recheck_val = db.query(check_query)
            prospect_id = recheck_val[0][0]
            return prospect_id


def adjust_names(mlb_id, fname, lname):
    names_dict = {
    "clark_trenton": ["Trent", "Grisham"],
    "deleon_juan": ["Juan", "De Leon"],
    "deleon_michael": ["Michael", "De Leon"],
    "eshelman_thomas": ["Tom", "Eshelman"],
    "gatewood_jacob": ["Jake", "Gatewood"],
    "groome_jason": ["Jay", "Groome"],
    "hall_dl": ["DL", "Hall"],
    "harrison_kj": ["KJ", "Harrison"],
    "machado_jonathan": ["Jonatan", "Machado"],
    "martinez_eddie": ["Eddy", "Martinez"],
    "pablo_martinez_julio": ["Julio Pablo", "Martinez"],
    "samuel_franco_wander": ["Wander", "Franco"],
    "sanchez_hudson": ["Hudson", "Potts"],
    "santillan_antonio": ["Tony", "Santillan"],
    "stewart_dj": ["DJ", "Stewart"],
    "yamamoto_jordan": ["Jordan", "Yamamoto"],
    "zapata_micker_adolfo": ["Micker", "Adolfo"],
    593423: ["Frankie", "Montas"],
    595222: ["Mike", "Gerber"],
    596001: ["Jakob", "Junis"],
    607188: ["Jake", "Faria"],
    621072: ["Nick", "Travieso"],
    621466: ["DJ", "Stewart"],
    645277: ["Ozzie", "Albies"],
    650520: ["Micker", "Adolfo"],
    650958: ["Michael", "De Leon"],
    656449: ["Jake", "Gatewood"],
    657141: ["Jordan", "Yamamoto"],
    660665: ["Juan", "De Leon"],
    663574: ["Tony", "Santillan"],
    663757: ["Trent", "Grisham"],
    664045: ["Tom", "Eshelman"],
    668888: ["Hudson", "Potts"],
    671054: ["Jonatan", "Machado"],
    677551: ["Wander", "Franco"],
    679881: ["Julio Pablo", "Martinez"],

    }

    if mlb_id in names_dict:
        fname, lname = names_dict.get(mlb_id)
        return fname, lname
    else:
        return fname, lname


def adjust_positions(mlb_id, positions):
    positions_dict = {
    "ryan_ryder": "RHP",
    669160: "RHP",
    "taylor_blake": "LHP",
    642130: "LHP",
    }

    if mlb_id in positions_dict:
        positions = positions_dict.get(mlb_id)
        return positions
    else:
        return positions


def adjust_birthdays(mlb_id, byear, bmonth, bday):
    birthday_dict = {
    "allen_logan":[1997,5,23],
    "aracena_ricky":[1997,10,2],
    "bradley_bobby":[1996,5,29],
    "burdi_zack":[1995,3,9],
    "burr_ryan":[1994,5,28],
    "castillo_diego":[1994,1,18],
    "cody_kyle":[1994,8,9],
    "deetz_dean":[1993,11,29],
    "diaz_lewin":[1996,11,19],
    "dietz_matthias":[1995,9,20],
    "ervin_phillip":[1992,7,15],
    "farmer_buck":[1991,2,20],
    "garcia_victor":[1999,9,16],
    "green_hunter":[1995,7,12],
    "hayes_kebryan":[1997,1,28],
    "hays_austin":[1995,7,5],
    "hill_brigham":[1995,7,8],
    "hudson_dakota":[1994,9,15],
    "jewell_jake":[1993,5,16],
    "justus_connor":[1994,11,2],
    "kirby_nathan":[1993,11,23],
    "knebel_corey":[1991,11,26],
    "lee_nick":[1991,1,13],
    "lopez_jose":[1993,9,1],
    "mathias_mark":[1994,8,2],
    "mitchell_calvin":[1999,3,8],
    "molina_leonardo":[1997,7,31],
    "murphy_brendan":[1999,1,2],
    "murphy_sean":[1994,10,10],
    "perez_joe":[1999,8,12],
    "quantrill_cal":[1995,2,10],
    "rainey_tanner":[1992,12,25],
    "riley_austin":[1997,4,2],
    "rodriguez_jose":[1995,8,29],
    "rosario_jeisson":[1999,10,22],
    "shipley_braden":[1992,2,22],
    "torres_gleyber":[1996,12,13],
    "tyler_robert":[1995,6,18],
    "uelmen_erich":[1996,5,19],
    "varsho_daulton":[1996,7,2],
    "wakamatsu_luke":[1996,10,10],
    "ward_taylor":[1993,12,14],
    "weigel_patrick":[1994,7,8],
    "whitley_forrest":[1997,9,15],
    "wise_carl":[1994,5,25],
    "woodford_jake":[1996,10,28],
    "zagunis_mark":[1993,2,5],

    }

    if mlb_id in birthday_dict:
        byear, bmonth, bday = birthday_dict.get(mlb_id)
        return byear, bmonth, bday
    else:
        return byear, bmonth, bday



if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument("--end_year",type=int,default=2018)
    parser.add_argument("--scrape_length",type=str,default="Current")

    args = parser.parse_args()
    
    initiate(args.end_year, args.scrape_length)



