from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper


# Calculates the defense only portion of WAR for every player in a years hitting register (pre-2017), or every player in `statistics_fielding` (2017 forward)


db = db('NSBL')


def process(year):
    if year <= 2016:
        register_war(year)
    else:
        statistics_war(year)

    # for year in range(2006,2017):
    #     register_war(year)

def register_war(year):
    player_q = """SELECT
player_name,
team_abb,
position,
age,
pa
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
        player_name, team_abb, position, age, pa = row
        pa = float(pa)
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['position'] = position

        bats = helper.get_hand(player_name)
        entry['bats'] = bats

        if bats == 'r':
            s_name = player_name
        else:
            s_name = player_name[:len(player_name)-1]

        
        entry['age'] = age
        entry['pa'] = pa
        entry['inn'] = None

        if year < 2011:
            defense = 0.0
            entry['defense'] = defense

            adj = float(helper.get_pos_adj(position.upper()))
            position_adj = adj*(pa/700)
            entry['position_adj'] = position_adj

        else:
            # changes Travis d'Arnoud to Travis d''Arnoud
            search_name = s_name.replace("'","''")
            rn_val, err_val, arm_val, pb_val = helper.get_def_values(search_name, position, year)

            #700 pa is a full season
            defense = float(pa)*(rn_val + err_val + arm_val + pb_val)/700

            entry['defense'] = defense
            adj = float(helper.get_pos_adj(position.upper()))
            position_adj = adj*(float(pa)/700)
            entry['position_adj'] = position_adj
            

        dwar = (defense+position_adj)/10.0

        entry['dWAR'] = dwar

        entries.append(entry)


    table = 'processed_compWAR_defensive'
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


def statistics_war(year):
    player_q = """SELECT
player_name,
team_id,
pos,
inn
FROM statistics_fielding
WHERE year = %s
"""
    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        entry['year'] = year
        player_name, team_id, position, inn = row
        entry['player_name'] = player_name

        search_name = player_name.replace("'","''")

        lookuptable = 'teams'
        team_abb = db.lookupValues("teams",("team_id","year",),(team_id,year),val="team_abb",operators=("=","="))[0]
        entry['team_abb'] = team_abb

        entry['position'] = position
        if position.lower() == 'p':
            continue
        else:

            entry['bats'] = None
            
            entry['age'] = None

            entry['pa'] = None
            entry['inn'] = inn

            rn_val, err_val, arm_val, pb_val = helper.get_def_values(search_name, position, year)

            #1450 innings is a full season
            defense = float(inn)*(rn_val + err_val + arm_val + pb_val)/1450

            entry['defense'] = defense
            adj = float(helper.get_pos_adj(position.upper()))
            position_adj = adj*(float(inn)/1450)
            entry['position_adj'] = position_adj

            dwar = (defense+position_adj)/10

            entry['dWAR'] = dwar

            entries.append(entry)


    table = 'processed_compWAR_defensive'
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
    