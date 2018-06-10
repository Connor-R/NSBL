from py_db import db
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import numpy as np
import argparse
import math
from scipy.stats import norm as NormDist, binom as BinomDist


# INCOMPLETE
# script that produces in-playoffs probability charts


db = db('NSBL')


def process(yr, _type):

    start_time = time()

    process_basic(yr, _type)

    process_wc(yr, _type)
    process_ds(yr, _type)
    process_cs(yr, _type)
    # process_ws(yr, _type)
    # process_champion(yr, _type)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "in_playoff_probabilities.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def process_basic(yr, _type):

    playoff_teams_qry = """SELECT
    team_abb, team_name,
    division, 
    top_seed, win_division
    FROM __playoff_probabilities
    JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb) t2 USING (team_abb, year, games_played)
    WHERE year = %s
    AND strength_type = '%s'
    AND win_ws > 0;"""

    playoff_teams_query = playoff_teams_qry % (yr, _type)
    # raw_input(playoff_teams_query)
    res = db.query(playoff_teams_query)

    entries = []
    for row in res:
        entry = {}
        team_abb, team_name, division, top_seed, win_division = row

        entry['team_abb'] = team_abb
        entry['team_name'] = team_name
        entry['year'] = yr
        entry['strength_type'] = _type
        entry['division'] = division
        entry['top_seed'] = top_seed
        entry['win_division'] = win_division

        entries.append(entry)

    db.insertRowDict(entries, '__temp_playoff_probabilities', insertMany=True, replace=True, rid=0,debug=1)
    db.conn.commit()

def process_wc(yr, _type):

    final_probs = {}
    for lg in ('AL', 'NL'):

        wc_qry = """SELECT team_abb, win_wc
    FROM __playoff_probabilities
    JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb) t2 USING (team_abb, year, games_played)
    WHERE YEAR = %s
    AND strength_type = '%s'
    AND win_wc > 0
    AND LEFT(division,2) = '%s'
    ORDER BY win_wc;"""

        wc_query = wc_qry % (yr, _type, lg)

        res = db.query(wc_query)

        teams = []
        prob_dicts = {}
        for row in res:
            team_abb, win_prob = row
            prob_dicts[team_abb] = win_prob
            teams.append(team_abb)
            final_probs[team_abb] = win_prob


        wc1 = db.query(wc_query)[0][0]
        wc2 = db.query(wc_query)[1][0]

        if lg == 'AL':
            wc_win = 'Tex'
            wc_lose = 'Sea'
        elif lg == 'NL': 
            wc_win = 'SD'
            wc_lose = 'ChN'

        final_probs[wc_win] = 1.0
        final_probs[wc_lose] = 0.0

    for tm, prob in final_probs.items():
        db.updateRow({'win_wc':prob},"__temp_playoff_probabilities",("team_abb","year","strength_type"),(tm,yr,_type),operators=['=','=','='])
        db.conn.commit()

def process_ds(yr, _type):
    query = """SELECT team_abb, win_division+IFNULL(win_wc,0) AS make_ds
FROM __temp_playoff_probabilities"""

    res = db.query(query)

    for row in res:
        team_abb, prob = row

        db.updateRow({'make_ds':prob},"__temp_playoff_probabilities",("team_abb","year","strength_type"),(team_abb,yr,_type),operators=['=','=','='])
        db.conn.commit()

def process_cs(yr, _type):
    for conf in ('AL', 'NL'):
        team_qry = """SELECT team_abb, top_seed, win_division-top_seed, win_wc
FROM __temp_playoff_probabilities
WHERE LEFT(division,2) = '%s'
AND make_ds > 0;"""

        team_query = team_qry % (conf)

        raw_input(team_query)

        team_res = db.query(team_query)









if __name__ == "__main__":  

    parser = argparse.ArgumentParser()
    parser.add_argument('--yr',default=2018)
    parser.add_argument('--_type',default='projected')

    args = parser.parse_args()

    process(args.yr, args._type)
    