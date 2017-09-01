from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper

# Calculates the pitching portion of WAR for every player in a years pitching register.


db = db('NSBL')


def process(year):
    pitching_war(year)

    # for year in range (2006, 2018):
    #     pitching_war(year)

def pitching_war(year):
    player_q = """SELECT
player_name,
team_abb,
position,
age, 
g, 
gs,
era,
ROUND(ip) + (10 * (ip - ROUND(ip)) / 3) as ip,
h, r, er, bb, k, hr
FROM register_pitching_primary
WHERE year = %s
"""

    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        player_name, team_abb, position, age, g, gs, era, ip, h, r, er, bb, k, hr = row
        entry['year'] = year
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['position'] = position
        throws = None
        entry['throws'] = throws
        entry['age'] = age
        entry['ip'] = ip

        team_abb = team_abb.upper()
        pf = float(helper.get_park_factors(team_abb))/float(100)
        entry['pf'] = pf

        if ip == 0:
            k_9 = 0.0
            if bb > 0:
                bb_9 = 99.0
                k_bb = 99.0
            else:
                bb_9 = 0.0
                k_bb = 0.0
            if hr > 0:
                hr_9 = 99.0
            else:
                hr_9 = 0.0
        else:
            k_9 = (float(k)/float(ip))*9
            bb_9 = (float(bb)/float(ip))*9
            hr_9 = (float(hr)/float(ip))*9
            if bb == 0:
                if k > 0:
                    k_bb = 99.0
                else:
                    k_bb = 0.0
            else:
                k_bb = (float(k)/float(bb))


        entry['k_9'] = k_9
        entry['bb_9'] = bb_9
        entry['k_bb'] = k_bb
        entry['hr_9'] = hr_9

        fip_const = float(helper.get_league_average_pitchers(year, 'fip_const'))
        FIP = ((((13*float(hr))+(3*float(bb))-(2*float(k)))/float(ip))+fip_const)
        entry['FIP'] = FIP

        park_FIP, FIP_min, FIP_WAR = helper.get_pitching_metrics(FIP, ip, year, pf, g, gs, 'fip')

        entry['park_FIP'] = park_FIP
        entry['FIP_minus'] = FIP_min
        entry['FIP_WAR'] = FIP_WAR


        ERA = float(era)
        entry['ERA'] = ERA

        park_ERA, ERA_min, ERA_WAR = helper.get_pitching_metrics(ERA, ip, year, pf, g, gs, 'era')

        entry['park_ERA'] = park_ERA
        entry['ERA_minus'] = ERA_min
        entry['ERA_WAR'] = ERA_WAR

        entries.append(entry)

    table = 'processed_WAR_pitchers'
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()

    # # for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process(args.year)
