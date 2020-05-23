import urllib2
from py_db import db
from bs4 import BeautifulSoup
from time import sleep, strftime, localtime # be nice
import re
import NSBL_helpers as helper
import subprocess
import os
import csv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

db = db('NSBL')

key_file = os.getcwd()+"/un_pw.csv"
key_list = {}
with open(key_file, 'rU') as f:
    mycsv = csv.reader(f)
    for row in mycsv:
        un, pw = row
        key_list[un]=pw

# Checks if standings have been updated, and if so, runs the weekly bash script

def initiate():

    standings_update = scrape_cur_standings()

    if standings_update == True:
        subprocess.call(['./NSBL_weekly_run.sh'])
        email_sub = "NSBL Updated [%s]" % (strftime("%Y-%m-%d %H:%M:%S", localtime()))
        email_msg = "Check http://thensbl.com/orgstand.htm for updated standings"
        email_msg += "\n\n\nUpdated Advanced Standings: http://connor-r.github.io/Tables/leaderboard_Standings.html"
        email_msg += "\nUpdated Leaderboard Changes: http://connor-r.github.io/Tables/leaderboard_Changes.html"
        email_msg += "\nUpdated Pitching Leaderboard: http://connor-r.github.io/Tables/leaderboard_Pitchers.html"
        email_msg += "\nUpdated Hitting Leaderboard: http://connor-r.github.io/Tables/leaderboard_Batters.html"
        email(email_sub, email_msg)

    else:
        print "No update - %s" % (strftime("%Y-%m-%d %H:%M:%S", localtime()))


def email(sub, mesg):
    email_address = "connor.reed.92@gmail.com"
    fromaddr = email_address
    toaddr = "connor.reed.92@gmail.com"
    bcc_addr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['BCC'] = bcc_addr
    msg['Subject'] = sub
    body = mesg
    msg.attach(MIMEText(mesg,'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, key_list.get(email_address))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def scrape_cur_standings():
    table_url = 'http://thensbl.com/orgstand.htm'

    tables = get_tables(table_url)

    for table in tables:
        standings_changed = False
        titles = table.find_all('tr', class_ = re.compile('dmrptsecttitle'))

        for title in titles:
            element = []
            tit = title.get_text()
            if tit == 'Divisional':
                sql_table = 'team_standings'

                rows = table.find_all('tr', class_ = re.compile('dmrptbody'))

                for row in rows:
                    element = []
                    for data in row:
                        if data.get_text() == '&nbsp':
                            element.append(None)
                        else:
                            #strip takes white space away from the front and end of a text string
                            element.append(data.get_text().strip()) 
                    
                    team_location_name = element[1]
                    wins = element[2]
                    losses = element[3]

                    if team_location_name is not None:
                        full_name = helper.get_team_name(team_location_name)


                        qry = """SELECT ts.year
                        , ts.team_name
                        , MAX(ts.games_played) AS gp
                        FROM team_standings ts
                        JOIN(
                            SELECT ts.team_name
                            , MAX(ts.year) AS year
                            FROM team_standings ts
                            WHERE 1
                                AND ts.team_name = '%s'
                            GROUP BY ts.team_name
                        ) a USING (team_name, year)
                        GROUP BY ts.team_name"""

                        prev_gp = db.query(qry % full_name)
                        prev_gp = prev_gp[0][2]

                        if int(wins)+int(losses) != prev_gp:
                            standings_changed = True

                        # print full_name, int(wins)+int(losses), prev_gp, standings_changed

    return standings_changed


def get_tables(table_url):
    sleep(0.5)
    html_team = urllib2.urlopen(table_url)
    soup_team = BeautifulSoup(html_team, "lxml")

    tables = soup_team.find_all('table', class_ = re.compile('dmrpt'))
    return tables



if __name__ == "__main__":     
   
    initiate()