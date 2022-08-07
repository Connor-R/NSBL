import urllib2
from py_db import db
from bs4 import BeautifulSoup
from time import sleep # be nice
import re
import argparse
import NSBL_helpers as helper


# Scrapes the various statistics from each team home page and writes the data to a MySQL db


db = db('NSBL')


invalid_names = {
    'Cincinatti Reds':'Cincinnati Reds',
    'World Champion Cardinals':'St. Louis Cardinals',
    'Los Angeles Angels of Anaheim':'Los Angeles Angels',
    'World Series Champion Washington Nationals':'Washington Nationals',
    }


player_mapper = {
}

qry = """SELECT wrong_name
, CONCAT(right_fname, ' ', right_lname) AS right_name
FROM name_mapper nm
;"""

res = db.query(qry)
for row in res:
    wrong, right = row
    player_mapper[wrong] = right


def initiate(end_year, scrape_length):
    if scrape_length == "All":
        current = False
        for year in range(2011, end_year):
            for team_id in range(1,31):
                url_base = "http://thensbl.com/%s/" % year
                url_ext = "tmindex%s.htm" % team_id
                url_index = url_base + url_ext

                html_ind = urllib2.urlopen(url_index)
                soup_ind = BeautifulSoup(html_ind,"lxml")
                team_name = (' '.join(soup_ind.find_all('h2')[1].get_text().split(" ")[1:]).split("\n")
                )[0].split("\r")[0]
                
                print url_index, team_name

                initiate_names(team_name, team_id, year, current, url_base)
    else:
        year = end_year
        current = True

        #Each week we truncate the current_rosters and re-fill. That's how we keep it current!
        db.query("TRUNCATE TABLE `current_rosters`")

        for team_id in range(1,31):
            url_base = "http://thensbl.com/"
            url_ext = "tmindex%s.htm" % team_id
            url_index = url_base + url_ext

            print url_index
            html_ind = urllib2.urlopen(url_index)
            soup_ind = BeautifulSoup(html_ind,"lxml")
            team_name = soup_ind.title.get_text()

            initiate_names(team_name, team_id, year, current, url_base)


def initiate_names(team_name, team_id, year, current, url_base):
    if team_name in invalid_names:
        team_name = invalid_names[team_name]

    check = "SELECT COUNT(*) FROM teams WHERE year = %s AND team_name = '%s' AND team_id = '%s';" % (year, team_name, team_id)
    check_val = db.query(check)[0][0]

    if check_val == 0:
        team_abb = raw_input('What is the team_abb for the %s %s? ' % (year, team_name))
        print str(year) + " - " + str(team_id) + " - " + team_name + " - " + team_abb
        team_entry = {"year":year,"team_id":team_id, "team_name": team_name, "team_abb": team_abb}
        team_table = "teams"
        db.insertRowDict(team_entry, team_table, insertMany=False, rid=0, replace=True)
        db.conn.commit()
        # raw_input("")

    process(team_id, year, current, url_base)


def process(team_id, year, current, url_base):
    # the 4 different scraping functions could be merged into 1 big function, but I found it easier to comprehend as separate functions, and scrape_ratings may be better off being re-written as 2 functions as well
    scrape_ratings(team_id, url_base, year, 'Batter Ratings')
    scrape_ratings(team_id, url_base, year, 'Pitcher Ratings')
    scrape_ratings(team_id, url_base, year, 'Fielding')

    # scrape_stats(team_id, url_base, year, 'batting')
    # scrape_stats(team_id, url_base, year, 'pitching')
    # scrape_stats(team_id, url_base, year, 'pitching_splits')

    scrape_fielding(team_id, url_base, year)

    if current == True:
        scrape_current_rosters(team_id, url_base, year, 'Batter Ratings')
        scrape_current_rosters(team_id, url_base, year, 'Pitcher Ratings')


def get_row_data(table, team_id, field=False, hand=""):
    # sleep(0.5)
    players = []
    rosters = table.find_all('tr', class_ = re.compile('dmrptbody'))
    
    # when we scrape defensive tables, only the first row is labeled with a position, so we create a pos variable to hold the position, and change it every time we encounter a new position
    if field == True:
        pos = ''
    for row in rosters:
        # create an empty list for adding a players attributes, and add the team_id to the list
        player = []
        player.append(team_id)


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

    # used for debugging
    # for player in players[:2]:
    #     print player
    #     print
    # raw_input("")

    return players


def get_tables(team_url):
    sleep(2.5)
    # print(team_url)
    try:
        html_team = urllib2.urlopen(team_url)
        soup_team = BeautifulSoup(html_team, "lxml")

        tables = soup_team.find_all('table', class_ = re.compile('dmrpt'))
        return tables
    except urllib2.URLError as e:
        print(team_url)
        print("\tError, (%s, %s) - waiting 30 seconds and trying again..." % (e.code, e.args))
        sleep(30)
        get_tables(team_url)


def input_data(ratings, year, sql_table, cats):
    print '\t' + sql_table
    entries = []
    for player in ratings:
        entry = {}
        entry['year'] = year
        for cat, val in zip(cats, player):
            if cat != 'foo':
                # entry[cat] = val #####
                if cat == 'player_name' and val is not None:
                    p_name = val.replace('*','').replace('#','')
                    if p_name in player_mapper:
                        p_name = player_mapper.get(p_name)
                    entry[cat] = p_name
                else:
                    entry[cat] = val
        if entry.get("player_name") not in ('Total', None, '', 'Other'):
            entries.append(entry)
    # raw_input(entries)
    if entries != []:
        db.insertRowDict(entries, sql_table, insertMany=True, rid=0, replace=True)
    db.conn.commit()


def scrape_stats(team_id, url_base, year, _type):
    if _type == 'batting':
        url_ext = "tm%s_tmbat.htm" % team_id
    elif _type == 'pitching':
        url_ext = "tm%s_tmpch.htm" % team_id
    elif _type == 'pitching_splits':
        url_ext = "tm%s_tmpch2.htm" % team_id

    team_url = url_base + url_ext

    tables = get_tables(team_url)

    for table in tables:
        title = table.find_all('tr', class_ = re.compile('dmrptsecttitle'))

        vsH = ""
        if _type == 'batting':
            if title[0].get_text() == 'Primary':
                sql_table = 'statistics_batting_primary'
                cats = ['team_id', 'foo', 'player_name', 'position', 'avg', 'obp', 'slg', 'g', 'ab', 'h', '2b', '3b', 'hr', 'r', 'rbi', 'bb', 'k', 'hbp', 'ibb', 'sb', 'cs']

            elif title[0].get_text() == 'Secondary':
                sql_table = 'statistics_batting_secondary'
                cats = ['team_id', 'foo', 'player_name', 'position', 'gs', 'pa', 'sh', 'sf', 'gdp', 'gw', 'ci', 'ops', 'rc', 'rc27', 'iso', 'tavg', 'sec', 'xbh', 'tb', 'chs', 'lhs']

            elif title[0].get_text() == 'Analytical':
                sql_table = 'statistics_batting_analytical'
                cats = ['team_id', 'foo', 'player_name', 'position', 'pa/g', 'ab/g', 'bip', 'babip', 'tbw', 'tbw/pa', 'tbwh', 'tbwh/pa', 'k/bb']

            elif title[0].get_text() == 'vs LHP':
                vsH = 'Left'
                sql_table = 'statistics_batting_splits'
                cats = ['team_id', 'vs_hand', 'foo', 'player_name', 'position', 'avg', 'obp', 'slg', 'ops', 'ab', 'h', '2b', '3b', 'hr', 'rbi', 'bb', 'k']

            elif title[0].get_text() == 'vs RHP':
                vsH = 'Right'
                sql_table = 'statistics_batting_splits'
                cats = ['team_id', 'vs_hand', 'foo', 'player_name', 'position', 'avg', 'obp', 'slg', 'ops', 'ab', 'h', '2b', '3b', 'hr', 'rbi', 'bb', 'k']

        elif _type == 'pitching':
            if title[0].get_text() == 'Primary':
                sql_table = 'statistics_pitching_primary'
                cats = ['team_id', 'foo', 'player_name', 'position', 'era', 'w', 'l', 'sv', 'g', 'gs', 'cg', 'sho', 'ip', 'h', 'r', 'er', 'bb', 'k', 'hr', 'gdp', 'bf']

            elif title[0].get_text() == 'Secondary':
                sql_table = 'statistics_pitching_secondary'
                cats = ['team_id', 'foo', 'player_name', 'position', 'sb', 'cs', 'ibb', 'hbp', 'wp', 'bk', 'sh', 'sf', 'ci', 'h/9', 'bb/9', 'r/9', 'k/9', 'hr/9', 'k/bb', 'pch/g', 'str_pct']

            elif title[0].get_text() == 'Analytical':
                sql_table = 'statistics_pitching_analytical'
                cats = ['team_id', 'foo', 'player_name', 'position', 'ops', 'whip', 'bip', 'babip', 'tbw', 'tbw/bf', 'tbwh', 'tbwh/bf', 'rc', 'rc27', 'rcera', 'cera']

            elif title[0].get_text() == 'Start':
                sql_table = 'statistics_pitching_rates_start'
                cats = ['team_id', 'foo', 'player_name', 'position', 'gs', 'cg', 'cg_pct', 'sho', 'qs', 'qs_pct', 'rs', 'rs/g', 'rl', 'rls', 'rl_pct']

            elif title[0].get_text() == 'Relief':
                sql_table = 'statistics_pitching_rates_relief'
                cats = ['team_id', 'foo', 'player_name', 'position', 'svo', 'sv', 'sv_pct', 'bs', 'bs_pct', 'hld', 'ir', 'irs', 'ir_pct', 'g', 'gr', 'gf']

        elif _type == 'pitching_splits':
            if title[0].get_text() == 'Primary':
                sql_table = 'statistics_pitching_splits_primary'
                cats = ['team_id', 'foo', 'player_name', 'position', 'avg', 'obp', 'slg', 'ab', 'h', '2b', '3b', 'hr', 'tb', 'hbp', 'bb', 'ibb', 'k', 'sb', 'cs']

            elif title[0].get_text() == 'vs LHB':
                vsH = 'Left'
                sql_table = 'statistics_pitching_splits'
                cats = ['team_id', 'vs_hand', 'foo', 'player_name', 'position', 'avg', 'obp', 'slg', 'ops', 'ab', 'h', '2b', '3b', 'hr', 'rbi', 'hbp', 'bb', 'ibb', 'k', 'sh', 'sf']

            elif title[0].get_text() == 'vs RHB':
                vsH = 'Right'
                sql_table = 'statistics_pitching_splits'
                cats = ['team_id', 'vs_hand', 'foo', 'player_name', 'position', 'avg', 'obp', 'slg', 'ops', 'ab', 'h', '2b', '3b', 'hr', 'rbi', 'hbp', 'bb', 'ibb', 'k', 'sh', 'sf']

            else:
                continue

        ratings = get_row_data(table, team_id, hand = vsH)

        input_data(ratings, year, sql_table, cats)


def scrape_fielding(team_id, url_base, year):
    url_ext = "tm%s_tmfld.htm" % team_id

    team_url = url_base + url_ext

    tables = get_tables(team_url)

    for table in tables:
        title = table.find_all('tr', class_ = re.compile('dmrptsecttitle'))

        if title[0].get_text() == 'Primary':
            sql_table = 'statistics_fielding'
            cats = ['team_id', 'pos', 'foo', 'foo', 'player_name', 'g', 'gs', 'inn', 'po', 'a', 'e', 'dp', 'tc', 'f_pct', 'pb', 'sb', 'cs', 'sb_pct', 'pk']
            ratings = get_row_data(table, team_id, field = True)

            input_data(ratings, year, sql_table, cats)

        else:
            continue


def scrape_ratings(team_id, url_base, year, rating_type):
    url_ext = "tm%s_tmroster.htm" % team_id

    team_url = url_base + url_ext

    tables = get_tables(team_url)

    for table in tables:
        title = table.find_all('tr', class_ = re.compile('dmrptsecttitle'))

        if title[0].get_text() == rating_type:

            if rating_type == "Batter Ratings":
                sql_table = "ratings_batting"
                cats = ['foo', 'foo', 'player_name', 'position', 'bats', 'age', 'vsL_avg', 'vsL_pwr', 'vsR_avg', 'vsR_pwr', 'bunt_sac', 'bunt_hit', 'run', 'steal', 'jump', 'injury', 'clutch']
            
            elif rating_type == "Pitcher Ratings":
                sql_table = "ratings_pitching"
                cats = ['foo', 'foo', 'player_name', 'position', 'throws', 'age', 'vsL_avg', 'vsR_avg', 'bunt_sac', 'bunt_hit', 'run', 'steal', 'jump', 'dur_s', 'dur_r', 'hld', 'wp', 'bk', 'gb_pct', 'jam', 'injury']

            elif rating_type == "Fielding":
                sql_table = "ratings_fielding"
                cats = ['foo', 'foo', 'player_name', 'position', 'p', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf', 'thr_of', 'thr_c', 'pb']

            ratings = get_row_data(table, team_id)

            input_data(ratings, year, sql_table, cats)

        else:
            continue


def scrape_current_rosters(team_id, url_base, year, rating_type):
    url_ext = "tm%s_tmroster.htm" % team_id

    team_url = url_base + url_ext

    tables = get_tables(team_url)

    for table in tables:
        title = table.find_all('tr', class_ = re.compile('dmrptsecttitle'))

        if title[0].get_text() == rating_type:

            if rating_type == "Batter Ratings":
                sql_table = "current_rosters"
                cats = ['team_id', 'foo', 'player_name', 'position', 'foo', 'age', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo']
            
            elif rating_type == "Pitcher Ratings":
                sql_table = "current_rosters"
                cats = ['team_id', 'foo', 'player_name', 'position', 'foo', 'age', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo']

            else:
                continue

            ratings = get_row_data(table, team_id)

            input_data(ratings, year, sql_table, cats)

        else:
            continue


if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--end_year',type=int,default=2022)
    parser.add_argument('--scrape_length',type=str,default="Current")

    args = parser.parse_args()
    
    initiate(args.end_year, args.scrape_length)

