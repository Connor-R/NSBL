from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper


# Calculates the offense only portion of WAR for every player in a years hitting register.

db = db('NSBL')

def process(year):
    offensive_war(year)

    # if year >= 2017:
    #     multi_team_war(year)

    # for year in range (2006, 2017):
    #     offensive_war(year)
    #     if year >= 2017:
    #         multi_team_war(year)


def offensive_war(year):
    player_q = """SELECT
player_name,
team_abb,
position,
age,
pa,
ab,
(h-2b-3b-hr) as 1b, 2b, 3b, hr, r, rbi, bb, k, hbp, sb, cs, ops, babip
FROM register_batting_primary
JOIN register_batting_secondary USING (year, player_name, team_abb, position, age)
JOIN register_batting_analytical USING (year, player_name, team_abb, position, age)
WHERE year = %s
"""
    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        entry['year'] = year
        player_name, team_abb, position, age, pa, ab, _1b, _2b, _3b, hr, r, rbi, bb, k, hbp, sb, cs, ops, babip = row
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['position'] = position
        if player_name[len(player_name)-1:] == "*":
            bats = 'l'
        elif player_name[len(player_name)-1:] == "#":
            bats = 's'
        else:
            bats = 'r'
        entry['bats'] = bats
        
        entry['age'] = age

        entry['pa'] = pa

        team_abb = team_abb.upper()
        pf = float(helper.get_park_factors(team_abb))/float(100)
        entry['pf'] = pf
        entry['ops'] = ops
        entry['babip'] = babip


        foo, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR = helper.get_offensive_metrics(year, pf, pa, ab, bb, hbp, _1b, _2b, _3b, hr, sb, cs)

        entry['wOBA'] = wOBA
        entry['park_wOBA'] = park_wOBA
        entry['OPS_plus'] = OPS_plus
        entry['wrc'] = wrc
        entry['wRC_27'] = wrc27
        entry['wRC_plus'] = wRC_plus
        entry['raa'] = raa
        entry['oWAR'] = oWAR

        entries.append(entry)


    table = 'processed_compWAR_offensive'
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process(args.year)
    