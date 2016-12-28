from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper

# Goes through the list of projected pitchers and projects their WAR


db = db('NSBL')

def process(year):
    # calculate_war(year)

    for year in range(2011,2017):
        calculate_war(year)


def calculate_war(year):
    player_q = """SELECT
player_name,
team_abb,
g, 
gs,
era,
ip,
h, r, er, bb, so, hr
FROM zips_pitching_%s
"""
    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        player_name, team_abb, g, gs, era, ip, h, r, er, bb, k, hr = row


        team_abb = team_abb.upper()
        pf = float(helper.get_park_factors(team_abb))/float(100)

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


        fip_const = float(helper.get_league_average_pitchers(year-1, 'fip_const'))
        FIP = ((((13*float(hr))+(3*float(bb))-(2*float(k)))/float(ip))+fip_const)
        park_FIP, FIP_min, FIP_WAR = helper.get_pitching_metrics(FIP, ip, year-1, pf, g, gs, 'fip')

        ERA = float(era)
        park_ERA, ERA_min, ERA_WAR = helper.get_pitching_metrics(ERA, ip, year-1, pf, g, gs, 'era')

        entry['year'] = year
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['pf'] = pf
        entry['ip'] = ip
        entry['k_9'] = k_9
        entry['bb_9'] = bb_9
        entry['k_bb'] = k_bb
        entry['hr_9'] = hr_9
        entry['FIP'] = FIP
        entry['park_FIP'] = park_FIP
        entry['FIP_minus'] = FIP_min
        entry['FIP_WAR'] = FIP_WAR
        entry['ERA'] = era
        entry['park_ERA'] = park_ERA
        entry['ERA_minus'] = ERA_min
        entry['ERA_WAR'] = ERA_WAR

        entries.append(entry)


    table = 'zips_processed_WAR_pitchers_%s' % year
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2011)
    args = parser.parse_args()
    
    process(args.year)
