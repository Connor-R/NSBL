from py_db import db
import argparse
from decimal import Decimal


# Goes through the list of offensive players and grabs their defensive data


db = db('NSBL')


def process(year):
    calculate_war(year)

    # for year in range(2006,2017):
    #     calculate_war(year)


def calculate_war(year):
    player_q = """SELECT
team_abb,
player_name,
position,
bats,
age,
pa,
oWAR
FROM processed_compWAR_offensive
WHERE year = %s
"""
    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        entry['year'] = year
        team_abb, player_name, position, bats, age, pa, oWAR = row

        entry['team_abb'] = team_abb
        entry['player_name'] = player_name
        entry['position'] = position
        entry['bats'] = bats
        entry['age'] = age
        entry['pa'] = pa
        entry['oWAR'] = oWAR

        team_q = "AND team_abb = '%s'" % team_abb
        if year >= 2017:
            if team_abb == '':
                team_q = ''
            if player_name[len(player_name)-1:] == "*":
                s_name = player_name[:len(player_name)-1]
            elif player_name[len(player_name)-1:] == "#":
                s_name = player_name[:len(player_name)-1]
            else:
                s_name = player_name
        else:
            s_name = player_name

        # changes Travis d'Arnoud to Travis d''Arnoud
        search_name = s_name.replace("'","''")

        def_q = """SELECT
SUM(defense), 
SUM(inn) AS inn,
SUM(pa),
SUM(position_adj),
SUM(dWAR)
FROM processed_compWAR_defensive
WHERE player_name = '%s'
AND year = %s
%s
"""
        def_qry = def_q % (search_name, year, team_q)
        def_query = db.query(def_qry)


        if def_query[0] != (None, None, None, None, None):
            defense, inn, d_pa, position_adj, dWAR = def_query[0]
            entry['defense'] = defense

            pa_games = 162*(float(pa)/700)
            ip_games = float(inn)/9
            dh_adj = -17.5*((pa_games - ip_games)/150.0)

            if (pa_games/ip_games) < 1.2:
                dh_adj = 0.0

            entry['position_adj'] = float(position_adj) + dh_adj
            dWAR_adj = (float(defense) + float(position_adj) + dh_adj)/10.0
            entry['dWAR'] = dWAR_adj

            if inn is not None:
                replacement = 20.0*(float(pa)/700)
            else:
                replacement = 20.0*(float(d_pa)/700)

            entry['replacement'] = replacement
        else:
            # if a player hasn't played defense, we treat them as a full-time DH
            entry['defense'] = 0.0
            position_adj = (float(pa)/700)*(-17.5)
            entry['position_adj'] = position_adj
            dWAR = float(position_adj)/10.0
            entry['dWAR'] = dWAR
            replacement = 20.0*(float(pa)/700)
            entry['replacement'] = replacement 

        repWAR = float(replacement)/10.0
        WAR = float(oWAR) + float(dWAR_adj) + float(repWAR)
        entry['WAR'] = WAR

        # print entry
        entries.append(entry)

    table = 'processed_WAR_hitters'
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
    