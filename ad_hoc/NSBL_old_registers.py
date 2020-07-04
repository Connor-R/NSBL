import urllib2
from py_db import db
from bs4 import BeautifulSoup
import argparse
from time import sleep # be nice
import re
import os
import NSBL_helpers as helper


# Parses the yearly registers from the html files from Joe and writes the data to a MySQL db


db = db('NSBL')


base_url = "http://thensbl.com/"


def initiate():
    for year in range (2006, 2017):
        print year
        process(year)


def process(year):
    scrape_registers(year)


def get_row_data(table, field=False, hand=""):
    # sleep(0.5)
    players = []
    rosters = table.find_all('tr', class_ = re.compile('dmrptbody'))
    
    # when we scrape defensive tables, only the first row is labeled with a position, so we create a pos variable to hold the position, and change it every time we encounter a new position
    if field == True:
        pos = ''
    for row in rosters:
        # create an empty list for adding a players attributes
        player = []
        if field == True:
            if row.get_text()[0] != '&':
                # row.td gets the soup for the first part of the tree with the td tag
                pos =  row.td.get_text()
            player.append(pos)

        # for split statistics
        if hand != "":
            player.append(hand)

        # &nbsp is how empty cells are labeled
        for data in row:
            if data.get_text() == '&nbsp':
                player.append(None)
            else:
                #strip takes white space away from the front and end of a text string
                player.append(data.get_text().strip()) 
        players.append(player)

    # # used for debugging
    # for player in players[:30]:
    #     print player
    #     print
    # raw_input("")

    return players


def get_tables(table_url):
    # sleep(0.5)
    html_team = urllib2.urlopen(table_url)
    soup_team = BeautifulSoup(html_team, "lxml")

    tables = soup_team.find_all('table', class_ = re.compile('dmrpt'))
    return tables


def input_data(ratings, sql_table, cats, year):
    print '\t' + sql_table
    entries = []
    for player in ratings:
        entry = {}
        entry['year'] = year
        for cat, val in zip(cats, player):
            # any category we aren't interested in recording, we mark as foo
            if cat != 'foo':
                # entry[cat] = val #####
                if cat == 'player_name' and val is not None:
                    entry[cat] = val.replace('*','').replace('#','')
                else:
                    entry[cat] = val



        if (entry.get("player_name") not in ('Total', None, '', 'Other') and entry.get("team_abb") not in ('Total', None, '', 'Other')):
            entries.append(entry)
        elif entry.get("team_name") not in ('Total', None, '', 'Other'):

            full_name = helper.get_team_name(entry.get("team_name"), year)
            entry['team_name'] = full_name
            if sql_table == 'team_standings':
                entry['games_played'] = int(entry.get('w')) + int(entry.get('l'))
            entries.append(entry)


    # used for debugging
    # if entries != []:
    #     for entry in entries[0:30]:
    #         print '\t\t',
    #         print entry
    #     raw_input("")

    if entries != []:
        db.insertRowDict(entries, sql_table, insertMany=True, rid=0, replace=True)
    db.conn.commit() 


def scrape_registers(year):
    for _type in ('batting', 'pitching'):
        if _type == 'batting':
            ext = 'batting'

        elif _type == 'pitching':
            ext = 'pitching'

        table_url = 'file://'+os.getcwd()+'/NSBL_registers/%s_%s_register.htm' % (year, ext)
        print '\t', _type, '\t', table_url

        tables = get_tables(table_url)

        for table in tables:

            title = table.find_all('tr', class_ = re.compile('dmrptsecttitle'))

            vsH = ""
            if _type == 'batting':
                if title[0].get_text() == 'Primary':
                    sql_table = 'register_batting_primary'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'avg', 'obp', 'slg', 'ab', 'h', '2b', '3b', 'hr', 'r', 'rbi', 'hbp', 'bb', 'k', 'sb', 'cs']

                elif title[0].get_text() == 'Secondary':
                    sql_table = 'register_batting_secondary'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'gs', 'pa', 'sh', 'sf', 'gdp', 'ops', 'rc', 'rc27', 'iso', 'tavg', 'sec', 'xbh', 'tb']

                elif title[0].get_text() == 'Analytical':
                    sql_table = 'register_batting_analytical'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'pa/g', 'ab/g', 'bip', 'babip', 'tbw', 'tbw/pa', 'tbwh', 'tbwh/pa', 'k/bb']

                elif title[0].get_text() == 'vs LHP':
                    vsH = 'Left'
                    sql_table = 'register_batting_splits'
                    cats = ['vs_hand', 'player_name', 'team_abb', 'position', 'age',  'avg', 'obp', 'slg', 'ops', 'ab', 'h', '2b', '3b', 'hr', 'rbi', 'bb', 'k']

                elif title[0].get_text() == 'vs RHP':
                    vsH = 'Right'
                    sql_table = 'register_batting_splits'
                    cats = ['vs_hand', 'player_name', 'team_abb', 'position', 'age',  'avg', 'obp', 'slg', 'ops', 'ab', 'h', '2b', '3b', 'hr', 'rbi', 'bb', 'k']

            elif _type == 'pitching':
                if title[0].get_text() == 'Primary':
                    sql_table = 'register_pitching_primary'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'era', 'w', 'l', 'sv', 'g', 'gs', 'cg', 'sho', 'ip', 'h', 'r', 'er', 'bb', 'k', 'hr', 'gdp']

                elif title[0].get_text() == 'Secondary':
                    sql_table = 'register_pitching_secondary'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'sb', 'cs', 'ibb', 'hbp', 'wp', 'bk', 'sh', 'sf', 'h/9', 'bb/9', 'r/9', 'k/9', 'hr/9', 'k/bb', 'whip']

                elif title[0].get_text() == 'Analytical':
                    sql_table = 'register_pitching_analytical'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'ops', 'bip', 'babip', 'tbw', 'tbw/bf', 'tbwh', 'tbwh/bf', 'rc', 'rc27', 'rcera', 'cera']

                elif title[0].get_text() == 'Start':
                    sql_table = 'register_pitching_rates_start'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'gs', 'cg', 'cg_pct', 'sho', 'qs', 'qs_pct', 'rs', 'rs/g', 'rl', 'rls', 'rl_pct', 'pch/g', 'str_pct']

                elif title[0].get_text() == 'Relief':
                    sql_table = 'register_pitching_rates_relief'
                    cats = ['player_name', 'team_abb', 'position', 'age', 'svo', 'sv', 'sv_pct', 'bs', 'bs_pct', 'hld', 'ir', 'irs', 'ir_pct', 'g', 'gr', 'gf', 'pch/g', 'str_pct']



            ratings = get_row_data(table, hand = vsH)

            input_data(ratings, sql_table, cats, year)


if __name__ == "__main__":     
    parser = argparse.ArgumentParser()

    args = parser.parse_args()
    
    initiate()


