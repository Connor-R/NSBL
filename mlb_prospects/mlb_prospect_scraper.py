import requests
import urllib
import csv
import os
import sys
import datetime
import codecs
from time import time, sleep


from py_data_getter import data_getter
from py_db import db


db = db('NSBL')
getter = data_getter()

sleep_time = 1

base_url = 'http://m.mlb.com/gen/players/prospects/%s/playerProspects.json'
player_base_url = 'http://m.mlb.com/gen/players/prospects/%s/%s.json'
player2_base_url = "http://mlb.com/lookup/json/named.player_info.bam?sport_code='mlb'&player_id=%s"

def initiate():
    start_time = time()

    for year in range(2018,2019):

        url = base_url % year
        # raw_input(url)
        json = getter.get_url_data(url, "json")
        prospect_lists = json["prospect_players"]

        scrape_prospects(year, prospect_lists)

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nmlb_prospect_scraper.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def scrape_prospects(year, prospect_lists):

    list_cnt = 0
    for list_type in (prospect_lists):
        entries = []
        if list_type not in ('rule5', 'prospects', 'pdp', 'rhp', 'lhp', 'c', '1b', '2b', '3b', 'ss', 'of'):
        # if list_type in ('atl'):
            list_cnt += 1
            print '\n', list_cnt, year, list_type
            ind_list = prospect_lists[list_type]
            
            i = 0
            for player in ind_list:
                entry = {}
                i += 1
                sleep(sleep_time) # be nice
                player_id = player['player_id']
                player_url = player_base_url % (year, player_id)
                # raw_input(player_url)
                
                print str(player_id) + '\t',
                sys.stdout.flush()

                sleep(sleep_time)
                player_json = getter.get_url_data(player_url, "json")


                try:
                    player_info = player_json["prospect_player"]
                except TypeError:
                    print '\tTYPE_ERROR'+str(year)+str(player_id)
                    continue


                entry["year"] = year
                entry["rank"] = i
                entry["player_id"] = player_id
                entry["fname"] = player_info["player_first_name"]
                entry["lname"] = player_info["player_last_name"]
                entry["position"] = player_info["positions"]

                if entry["player_id"] in (669160,'ryan_ryder',):
                    entry["position"] = "RHP"

                if entry["player_id"] in ('taylor_blake',):
                    entry["position"] = "LHP"
                

                if list_type in ('int','draft'):
                    bats = player_info["bats"]
                    throws = player_info["thrw"]
                    try:
                        height = player_info["height"].replace('\"','').split('\'')
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
                        byear = None
                        bmonth = None
                        bday = None              

                else:
                    info_url = player2_base_url % player_id
                    # print '\t\t'+info_url

                    sleep(sleep_time)
                    info_json = getter.get_url_data(info_url, "json", json_unicode_convert=True)
                    # raw_input(info_json)
                    info_info = info_json["player_info"]["queryResults"]["row"]
                    dob = info_info["birth_date"]
                    byear = dob.split("-")[0]
                    bmonth = dob.split("-")[1]
                    bday = dob.split("-")[2].split("T")[0]

                    try:
                        bats = info_info["bats"]
                        throws = info_info["throws"]
                        height = int(info_info["height_feet"])*12+int(info_info["height_inches"])
                        weight = int(info_info["weight"])                  

                    except UnicodeDecodeError:
                        bats, throws, height, weight = (None, None, None, None)
                

                entry["bats"] = bats
                entry["throws"] = throws
                entry["height"] = height
                entry["weight"] = weight
                entry["birth_year"] = byear
                entry["birth_month"] = bmonth
                entry["birth_day"] = bday

                entry["team"] = player['team_file_code']
                drafted = player_info["drafted"]                

                if list_type == 'int':
                    drafted = None
                    try:
                        sign_text = player_info["signed"]
                        sign_value = sign_text.split(' - ')[1]
                        signed = sign_value
                    except IndexError:
                        signed = ''
                    try:
                        signed = int(signed.replace('$','').replace(',',''))
                    except ValueError:
                        signed = None

                    schoolcity = player_info["school"]
                    gradecountry = player_info["year"]
                    commit = None
                elif list_type == 'draft':
                    try:
                        signed = player_info["preseason20"].replace(' ','').replace(',','').replace('$','').split('-')[1]
                    except (KeyError, IndexError):
                        signed = player_info["signed"].replace(' ','').replace(',','').replace('$','')
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

                if list_type not in ('int', 'draft'):
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


                blurb = player_info["content"]["default"].replace('<b>','').replace('</b>','').replace('<br />','').replace('<p>','').replace('</p>','').replace('*','')
                entry["blurb"] = blurb

                entries.append(entry)


        if list_type == 'draft':
            table = '_draft_prospects'
        elif list_type == 'int':
            table = '_international_prospects'
        else:
            table = '_professional_prospects'

        if entries != []:
            for i in range(0, len(entries), 1000):
                db.insertRowDict(entries[i: i + 1000], table, insertMany=True, replace=True, rid=0,debug=1)
                db.conn.commit()



if __name__ == "__main__":     
    initiate()



