from py_db import db
import argparse
from decimal import Decimal


# Calculates the sum total of individual player WARs (for both hitters and pitchers) and writes it to the db


db = db('NSBL')


def initiate(year):
    print "processed_WAR_team", year
    process(year)

    # for year in range(2005,2021):
        # process(year)


def process(year):
    team_list_q = """
    SELECT team_abb
    FROM(
        SELECT team_abb FROM processed_WAR_hitters WHERE YEAR = %s
        UNION SELECT team_abb FROM processed_WAR_pitchers WHERE YEAR = %s
    ) combo
    WHERE team_abb != ''
    GROUP BY team_abb;
    """
    team_list_qry = team_list_q % (year, year)
    team_list = db.query(team_list_qry)

    entries = []
    for team in team_list:
        team_abb = team[0]

        entry = team_war(team_abb, year)
        entries.append(entry)


    if entries != []: 
        db.insertRowDict(entries, 'processed_WAR_team', replace=True, insertMany=True, rid=0)
    db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


def team_war(team_abb, year):
    entry = {}
    entry['year'] = year
    entry['team_abb'] = team_abb

    hitter_q = """SELECT
    SUM(defense),
    SUM(position_adj),
    SUM(dWAR),
    SUM(oWAR),
    SUM(replacement),
    SUM(WAR)
    FROM processed_WAR_hitters
    WHERE year = %s
    AND team_abb = '%s';
    """

    hitter_qry = hitter_q % (year, team_abb)

    hitter_data = db.query(hitter_qry)[0]

    defense, position_adj, dWAR, oWAR, replacement, hitter_WAR = hitter_data

    entry['defense'] = defense
    entry['position_adj'] = position_adj
    entry['dWAR'] = dWAR
    entry['oWAR'] = oWAR
    entry['replacement'] = replacement
    entry['hitter_WAR'] = hitter_WAR


    pitcher_q = """SELECT
    SUM(FIP_WAR),
    SUM(ERA_WAR)
    FROM processed_WAR_pitchers
    WHERE year = %s
    AND team_abb = '%s';
    """

    pitcher_qry = pitcher_q % (year, team_abb)

    pitcher_data = db.query(pitcher_qry)[0]

    FIP_WAR, ERA_WAR = pitcher_data

    entry['FIP_WAR'] = FIP_WAR
    entry['ERA_WAR'] = ERA_WAR


    total_fWAR = hitter_WAR + FIP_WAR
    total_rWAR = hitter_WAR + ERA_WAR

    entry['total_fWAR'] = total_fWAR
    entry['total_rWAR'] = total_rWAR

    return entry


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2018)
    args = parser.parse_args()
    
    initiate(args.year)
    

