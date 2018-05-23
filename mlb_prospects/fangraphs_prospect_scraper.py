import requests
import urllib2
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
import sys
from time import time, sleep, mktime
import argparse

from py_db import db

db = db("mlb_prospects")

sleep_time = 1
base_url = "https://www.fangraphs.com/scoutboard.aspx"
# current_page = 1
current_page = 1

start_time = time()

def initiate(end_year, scrape_length):
    if scrape_length == 'All':
        for year in range (2013, end_year+1):
            process(year)
    else:
        year = end_year
        process(year)


    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nfangraphs_prospect_scraper.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def process(year):
    for list_type, list_key in {"professional":"prospect","draft":"mlb","international":"int"}.items():

        if ((list_type=="professional" and year > 2016) or 
            (list_type=="draft" and year > 2014) or 
            (list_type=="international" and year > 2014)):
            process_prospect_list(year, list_type, list_key)
def process_prospect_list(year, list_type, list_key):
    players_per_page = 10
    list_url = base_url +"?draft=%s%s&page=1_%s" % (year, list_key, players_per_page)
    print "\n", year, list_type, list_url

    sleep(sleep_time)
    page_data = requests.get(list_url)
    soup = BeautifulSoup(page_data.content, "lxml")

    try:
        total_pages = soup.find(class_="rgWrap rgInfoPart").findAll("strong")
        pages_cnt = total_pages[1].getText()
    except AttributeError:
        pages_cnt = 1

    # for page in range(1 ,int(pages_cnt)+1):
    for page in range(current_page ,int(pages_cnt)+1):
        list_sub_url = base_url + "?draft=%s%s&page=%s_%s"% (year, list_key, page, players_per_page)
        print "\t", list_sub_url

        process_list_page(year, list_type, list_key, list_sub_url, page, players_per_page, players_per_page*int(pages_cnt))
def process_list_page(year, list_type, list_key, list_sub_url, page, players_per_page, max_players):
    sleep(sleep_time)
    page_data = requests.get(list_sub_url)
    soup = BeautifulSoup(page_data.content, "lxml")

    entries = []
    rows = soup.findAll(True, {"class":["rgRow","rgAltRow"]})
    for cnt, row in enumerate(rows):
        if list_type == "professional":
            process_professional(year, row, (page-1)*players_per_page+cnt+1, max_players)
            entry = None
        else:
            entry = process_amateur(year, row, list_type, (page-1)*players_per_page+cnt+1, max_players)

        if entry != None:
            entries.append(entry)

    if list_type == "draft":
        table = "fg_prospects_draft"
    elif list_type == "international":
        table = "fg_prospects_international"

    if entries != []:
        for i in range(0, len(entries), 10000):
            db.insertRowDict(entries[i: i + 10000], table, insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


def process_professional(year, row, cnt, max_players):
    entry = {}

    elements = row.findAll(True, {"class":["grid_line_regular", "grid_line_break"]})

    full_name = elements[0].getText()
    full_name, fname, lname = adjust_names2(full_name)

    prospect_url_base = "https://www.fangraphs.com/"
    if full_name == "Shohei Ohtani":
        prospect_url = "https://www.fangraphs.com/statss.aspx?playerid=19755&position=DH"
    else:
        try:
            prospect_url = prospect_url_base + row.find("a", href=True)["href"].split("&")[0]
        except TypeError:
            prospect_url = ""

    if "statss.aspx" not in prospect_url:
        # print "\n\n**ERROR TAG** NO BIRTHDAY", year, full_name, "\n\n"
        prospect_url = None

    print "\t\t", year, str(cnt) + " of " + str(max_players), full_name, "\t", prospect_url

    if prospect_url is not None:
        birth_year, birth_month, birth_day, overall_rank, team_rank, reported, scouting_dict = process_fangraphs_url(prospect_url)

        fg_id = prospect_url.split("playerid=")[-1]
        fg_id, birth_year, birth_month, birth_day = adjust_birthdays(fg_id, birth_year, birth_month, birth_day)
    
        prospect_id = add_prospect(fg_id, fname, lname, birth_year, birth_month, birth_day, "fg")
    else:
        birth_year, birth_month, birth_day, overall_rank, team_rank, reported, scouting_dict = None, None, None, None, None, None, None
        age = int(elements[7].getText())
        lower_year = year - age - 1
        upper_year = year - age + 1
        prospect_id, birth_year, birth_month, birth_day = fg_id_lookup(fname, lname, lower_year, upper_year)
        fg_id = str(year) + '_' + fname + '_' + lname

    entry["fg_id"] = fg_id 
    entry["prospect_id"] = prospect_id
    entry["year"] = year
    entry["birth_year"] = birth_year
    entry["birth_month"] = birth_month
    entry["birth_day"] = birth_day


    element_dict = {1:"team", 3:"top100", 4:"team_rank", 5:"FV", 6:"ETA", 9:"weight", 10:"bats", 11:"throws", 12:"signed"}
    for i, e in enumerate(elements):
        if i in element_dict:
            i_val = element_dict.get(i)
            entry[i_val] = e.getText()

    entry["full_name"] = full_name
    entry["fname"] = fname
    entry["lname"] = lname

    if entry["top100"] == 0:
        entry["top100"] == None

    try:
        position = elements[2].getText()
    except TypeError:
        position = None
    position = adjust_positions(full_name, position)
    entry["position"] = position

    try:
        signed_from = elements[13].getText()
    except TypeError:
        signed_from = None
    entry["signed_from"] = signed_from

    try:
        height = elements[8].getText()
        height = int(height.split("'")[0])*12 + int(height.split("'")[1].split("\"")[0])
    except ValueError:
        height = 0
    entry["height"] = height

    try:
        video = row.find(class_ = "fancybox-media")["href"].strip()
    except TypeError:
        video = None
    entry["video"] = video

    if scouting_dict is not None:
        process_scouting_grades(reported, prospect_id, scouting_dict)

    db.insertRowDict(entry, "fg_prospects_professional", replace=True, debug=1)


def process_amateur(year, row, list_type, cnt, max_players):
    entry = {"year":year}

    elements = row.findAll(True, {"class":["grid_line_regular", "grid_line_break"]})

    if list_type == "draft":
        element_dict = {0:"rank", 3:"draft_age", 5:"weight", 6:"bats", 7:"throws", 8:"school", 9:"fv", 11:"video"}
        height_index = 4
        blurb_index = 10
    elif list_type == "international":
        element_dict = {0:"rank", 3:"j2_age", 4:"country", 5:"height", 6:"weight", 7:"bats", 8:"throws", 9:"fv", 10:"risk", 11:"proj_team", 13:"video"}
        height_index = 5
        blurb_index = 12

    for i, e in enumerate(elements):
        if i in element_dict:
            i_val = element_dict.get(i)
            if i_val == "video":
                try:
                    url = e.find("a", href=True)["href"]
                except TypeError:
                    url = ""
                entry[i_val] = url
            else:
                entry[i_val] = e.getText()

    full_name = elements[1].getText()
    full_name, fname, lname = adjust_names2(full_name)
    print "\t\t", year, list_type, str(cnt) + " of " + str(max_players), full_name

    age = elements[3].getText()
    age = adjust_age2(full_name, year, list_type, age)
    try:
        lower_year, upper_year = est_birthday(age, year, list_type)
        est_years = str(lower_year) + "-" + str(upper_year)
        prospect_id, byear, bmonth, bday = fg_id_lookup(fname, lname, lower_year, upper_year)
    except ValueError:
        est_years = "0-0"
        prospect_id = 0

    try:
        height = elements[height_index].getText()
        height = int(height.split("'")[0])*12 + int(height.split("'")[1].split("\"")[0])
    except ValueError:
        height = 0

    position = elements[2].getText()
    position = adjust_positions2(full_name, position)

    try:
        blurb_split = "Report"+elements[1].getText()
        blurb = elements[blurb_index].getText().split(blurb_split)[1]
        blurb = "".join([i if ord(i) < 128 else "" for i in blurb])
    except IndexError:
        blurb = ""

    entry["full_name"] = full_name
    entry["fname"] = fname
    entry["lname"] = lname
    entry[element_dict.get(3)] = age
    entry["est_years"] = est_years
    entry["prospect_id"] = prospect_id
    entry["height"] = height
    entry["position"] = position
    entry["blurb"] = blurb

    return entry


def process_fangraphs_url(player_url):
    sleep(sleep_time)
    player_data = requests.get(player_url)
    player_utf_data = "".join([i if ord(i) < 128 else "" for i in player_data.content])

    player_soup = BeautifulSoup(player_utf_data, "lxml")

    birthdate = player_soup.find(class_ = "player-info-bio").getText().split("Birthdate: ")[1].split("(")[0].strip()
    birth_month, birth_day, birth_year = birthdate.split("/")

    try:
        report_info = player_soup.find(class_ = "prospects-report").find("span")
        report_string = str(report_info)
    except AttributeError:
        return birth_year, birth_month, birth_day, None, None, None, None

    team_rank, overall_rank, reported = None, None, None
    team_rank = report_string.split("Team Rank</strong>:")[1].split("<strong")[0].strip()
    overall_rank = report_string.split("Overall Rank</strong>:")[1].split("<strong")[0].strip()
    reported = report_string.split("Reported</strong>:")[1].split("<strong")[0].strip()

    scouting_table_soup = player_soup.find(class_ = "depth_chart")
    scouting_table = scouting_table_soup.findAll("tr")
    prospect_categories = scouting_table[0].findAll("th")
    prospect_values = scouting_table[1].findAll("td")

    cats = {}
    for i, cat in enumerate(prospect_categories):
        cats[i] = cat.getText()

    scouting_dict = {}
    vals = {}
    for i, val in enumerate(prospect_values):
        cat = cats.get(i)
        scouting_dict[cat] = val.getText()

    return birth_year, birth_month, birth_day, overall_rank, team_rank, reported, scouting_dict    
def adjust_positions(fg_id, positions):
    positions_dict = {
    }

    if fg_id in positions_dict:
        positions = positions_dict.get(fg_id)
        return positions
    else:
        return positions
def adjust_birthdays(fg_id, byear, bmonth, bday): 
    birthday_dict = {
    "14510": ["14510", 1993, 7, 1],
    "16401": ["16401", 1993, 12, 26],
    "sa293098": ["sa874117", 1995, 10, 2],
    "sa392969": ["sa829387", 1997, 2, 24],
    }

    if fg_id in birthday_dict:
        fg_id2, byear, bmonth, bday = birthday_dict.get(fg_id)
        return fg_id2,byear, bmonth, bday
    else:
        return fg_id, byear, bmonth, bday
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
def process_scouting_grades(reported, prospect_id, scouting_dict):
    entry = {}
    if "Hit" in scouting_dict:
        player_type = "hitters"
    elif ("Fastball" in scouting_dict or "Command" in scouting_dict):
        player_type = "pitchers"
    else:
        # print "\n\n**ERROR TAG** CORRUPTED GRADES", reported, prospect_id, scouting_dict, "\n\n"
        return None

    entry["year"] = reported
    entry["prospect_id"] = prospect_id

    hitter_cats = ["Hit", "GamePower", "Field", "RawPower", "Speed", "Throws"]
    pitcher_cats = ["Fastball", "Changeup", "Curveball", "Slider", "Cutter", "Splitter", "Command"]
    for k, v in scouting_dict.items():
        if player_type == "hitters":
            if k in hitter_cats:
                entry[k+"_present"] = v.split(" / ")[0].strip()
                entry[k+"_future"] = v.split(" / ")[1].strip()
            elif k != "Future Value":
                print "\n\n**ERROR TAG** NO CATEGORY", k, "\t", v, "\n\n"
        elif player_type == "pitchers":
            if k in pitcher_cats:
                entry[k+"_present"] = v.split(" / ")[0].strip()
                entry[k+"_future"] = v.split(" / ")[1].strip()
            elif k != "Future Value":
                entry["Other_present"] = v.split(" / ")[0].strip()
                entry["Other_future"] = v.split(" / ")[1].strip()

    table = "fg_grades_%s" % (player_type)
    db.insertRowDict(entry, table, replace=True, debug=1)
    db.conn.commit()
def adjust_age2(full_name, year, list_type, age):
    age_search = full_name + "_" + str(year) + "_" + str(list_type)

    ages_dict = {
    "Adrian Morejon_2016_international":17.3,

    }

    if age_search in ages_dict:
        age = ages_dict.get(age_search)
        return age
    else:
        return age
def adjust_positions2(full_name, position):
    names_dict = {
    }
 
    if full_name in names_dict:
        position = names_dict.get(full_name)
        return position
    else:
        return position
def est_birthday(age, year, list_type):
    if list_type == "draft":
        reference_date = datetime(year=year, month=06, day=15)
    elif list_type == "international":
        reference_date = datetime(year=year, month=07, day=02)

    days = (float(age)*365.25)
    birthday_est = reference_date - timedelta(days=days)

    est_year = birthday_est.year
    print year, age, est_year, birthday_est.month
    if (birthday_est.month >= 5 or birthday_est.month <= 8):
        lower_year = est_year - 1
        upper_year = est_year + 1
    elif (birthday_est.month > 8):
        lower_year = est_year
        upper_year = est_year + 1
    else:
        lower_year = est_year - 1
        upper_year = est_year

    return lower_year, upper_year
def fg_id_lookup(fname, lname, lower_year, upper_year):
    search_qry = """SELECT prospect_id, birth_year, birth_month, birth_day, COUNT(*)
    FROM professional_prospects 
    WHERE birth_year >= %s 
    AND birth_year <= %s
    AND ((mlb_lname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",mlb_lname,"%%")) OR (fg_lname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",fg_lname,"%%")))
    AND ((mlb_fname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",mlb_fname,"%%")) OR (fg_fname LIKE "%%%s%%") OR ("%s" LIKE CONCAT("%%",fg_fname,"%%")))
    ;"""

    search_query = search_qry % (lower_year, upper_year, lname, lname, lname, lname, fname, fname, fname, fname)
    player_id, byear, bmonth, bday, player_cnt = db.query(search_query)[0]

    if player_cnt == 1:
        prospect_id = player_id
    else:
        prospect_id = 0
        byear, bmonth, bday = None, None, None

    id_search = fname+lname
    id_dict = {
    "AustinBeck": 2061,
    "ChrisShaw": 1541,
    }
    if id_search in id_dict:
        prospect_id = id_dict.get(id_search)

    return prospect_id, byear, bmonth, bday
def adjust_names2(full_name):
    names_dict = {
    "Abraham Gutierrez": ["Abrahan", "Gutierrez"],
    "Adam Brett Walker": ["Adam Brett", "Walker"],
    "D.J. Stewart": ["DJ", "Stewart"],
    "Fernando Tatis, Jr.": ["Fernando", "Tatis Jr."],
    "Hoy Jun Park": ["Hoy Jun", "Park"],
    "Jeison Rosario": ["Jeisson", "Rosario"],
    "Jonathan Machado": ["Jonatan", "Machado"],
    "Luis Alejandro Basabe": ["Luis Alejandro", "Basabe"],
    "Luis Alexander Basabe": ["Luis Alexander", "Basabe"],
    "M.J. Melendez": ["MJ", "Melendez"],
    "Mc Gregory Contreras": ["Mc Gregory", "Contreras"],
    "Michael Soroka": ["Mike", "Soroka"],
    "Nate Kirby": ["Nathan", "Kirby"],
    "Onil Cruz": ["Oneil", "Cruz"],
    "Roland Bolanos": ["Ronald", "Bolanos"],
    "T.J. Friedl": ["TJ", "Friedl"],
    "Thomas Eshelman": ["Tom", "Eshelman"],
    "TJ Zeuch": ["T.J.", "Zeuch"],
    "Trenton Clark": ["Trent", "Grisham"],
    "Vladimir Guerrero, Jr.": ["Vladimir", "Guerrero Jr."],
    "Yordy Barley": ["Jordy", "Barley"],
    }

    if full_name in names_dict:
        fname, lname = names_dict.get(full_name)
        full_name = fname + " " + lname
        return full_name, fname, lname
    else:
        fname, lname = [full_name.split(" ")[0], " ".join(full_name.split(" ")[1:])]
        return full_name, fname, lname

if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument("--end_year",type=int,default=2018)
    parser.add_argument("--scrape_length",type=str,default="Current")

    args = parser.parse_args()
    
    initiate(args.end_year, args.scrape_length)


