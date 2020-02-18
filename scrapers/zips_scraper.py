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


db = db("NSBL")


sleep_time = 5
initial_url = "https://blogs.fangraphs.com/2020-zips-projections-arizona-diamondbacks/"


start_time = time()


def initiate(year):
    page_data = requests.get(initial_url)
    soup = BeautifulSoup(page_data.content, "lxml")


    team_links = soup.find_all("div", attrs={"class":"box-team"})

    urls = []
    for tl in team_links:
        links = tl.find_all("a", href=True)
        # raw_input(links)
        for link in links:
            # raw_input(link)
            url = link['href']
            # print url
            team_abb = link.getText()

            if ("/" + str(year) + "-zips" in url) or ("/zips-" + str(year) in url):
                urls.append({team_abb:url})

    # raw_input(urls)
    process_urls(urls, year)

def process_urls(urls, year):
    print year
    for teamcnt, team_pair in enumerate(urls):
        for tm, url in team_pair.items():
            print '\t', str(teamcnt+1), tm, '-', url
            
            tm_list = []
            tm_query = db.query("SELECT DISTINCT team_abb FROM zips_fangraphs_batters_counting WHERE year = %s" % (year))
            for t in tm_query:
                tm_list.append(t[0])
            if tm in tm_list:
                continue

            sleep(sleep_time)
            team_data = requests.get(url)
            team_soup = BeautifulSoup(team_data.content, "lxml")

            postmeta_date = team_soup.find(class_="postmeta").findAll("div")[-1].getText()
            post_date = parse(postmeta_date).strftime("%Y-%m-%d")

            tables = team_soup.findAll("table", {"class": ["sortable", "sortable table-equal-width", "table-equal-width"]})
            print len(tables)
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

                # raw_input(table)
                headers = table.find("tr")
                # raw_input(headers)

                headers = headers.findAll()

                for h in headers:
                    cat = h.getText().replace('/','_').replace('+','_Plus').replace('-','_Minus').replace('No. 1 Comp','Top_Comp').replace('%','_Pct')
                    cats.append(cat)

                # print cats
                rows = table.findAll("tr")

                for r in rows:
                    # print r
                    # print r.get("class")
                    # raw_input("")
                    if r.get("class") is None:
                        entry = {}
                        entry["year"] = year
                        entry["team_abb"] = tm
                        entry["post_date"] = post_date
                        atts = r.findAll("td")
                        # raw_input(atts)
                        if atts != []:
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

    parser.add_argument("--year",type=int,default=2020)
    args = parser.parse_args()
    
    initiate(args.year)


