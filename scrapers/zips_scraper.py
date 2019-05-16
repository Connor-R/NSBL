import pdb
import requests
import urllib2
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
import sys
from time import time, sleep, mktime
import argparse
from dateutil.parser import parse


from py_db import db
import prospect_helper as helper


db = db("NSBL")


sleep_time = 5
initial_url = "https://blogs.fangraphs.com/2019-zips-projections-los-angeles-dodgers/"


start_time = time()


def initiate(year):
    page_data = requests.get(initial_url)
    soup = BeautifulSoup(page_data.content, "lxml")

    team_links = soup.find(class_="box-team").findAll("a", href=True)

    urls = []
    for link in team_links:
        url = link['href']
        team_abb = link.getText()

        if "/" + str(year) + "-zips" in url:
            urls.append({team_abb:url})

    process_urls(urls, year)

def process_urls(urls, year):
    print year
    for teamcnt, team_pair in enumerate(urls):
        for tm, url in team_pair.items():
            print '\t', str(teamcnt+1), tm
            
            if tm != 'CHW':
                continue

            sleep(sleep_time)
            team_data = requests.get(url)
            team_soup = BeautifulSoup(team_data.content, "lxml")

            postmeta_date = team_soup.find(class_="postmeta").findAll("div")[-1].getText()
            post_date = parse(postmeta_date).strftime("%Y-%m-%d")

            tables = team_soup.findAll("table", {"class": " sortable"})

            for i, table in enumerate(tables):
                entries = []
                cats = []
                if i == 0 :
                    db_table = "zips_fangraphs_batters_counting"
                elif i == 1:
                    db_table = "zips_fangraphs_batters_rate"
                elif i == 2:
                    db_table = "zips_fangraphs_pitchers_counting"
                elif i == 3:
                    db_table = "zips_fangraphs_pitchers_rate"

                print '\t\t', db_table

                headers = table.find(class_="sort").findAll()

                for h in headers:
                    cat = h.getText().replace('/','_').replace('+','_Plus').replace('-','_Minus').replace('No. 1 Comp','Top_Comp').replace('%','_Pct')
                    cats.append(cat)

                rows = table.findAll("tr")

                for r in rows:
                    if r.get("class") is None:
                        entry = {}
                        entry["year"] = year
                        entry["team_abb"] = tm
                        entry["post_date"] = post_date
                        atts = r.findAll("td")
                        for j, att in enumerate(atts):
                            fld = att.getText()
                            fld = "".join([i if ord(i) < 128 else "" for i in fld])
                            entry[cats[j]] = fld

                        # print '\t\t\t', entry
                        if entry["Player"] != "":
                            entries.append(entry)

                if entries != []:
                    for i in range(0, len(entries), 1000):
                        db.insertRowDict(entries[i: i + 1000], db_table, insertMany=True, replace=True, rid=0,debug=1)
                        db.conn.commit()

if __name__ == "__main__":     
    parser = argparse.ArgumentParser()

    parser.add_argument("--year",type=int,default=2019)
    args = parser.parse_args()
    
    initiate(args.year)


