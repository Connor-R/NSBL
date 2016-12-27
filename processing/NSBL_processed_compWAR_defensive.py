from py_db import db
import argparse
from decimal import Decimal


# Calculates the defense only portion of WAR for every player in a years hitting register (pre-2017), or every player in `statistics_fielding` (2017 forward)


db = db('NSBL')
pos_adj = {
    "P":60.0,
    "C":12.5,
    "1B":-12.5,
    "2B":2.5,
    "3B":2.5,
    "SS":7.5,
    "LF":-7.5,
    "CF":2.5,
    "RF":-7.5,
    "DH":-17.5,
    "PH":-17.5,
    "IF":2.5,
    "":0
}

# [range, error, arm, passed ball]
pos_formula = {
    "P":[0.0,0.0,0.0,0.0],
    "C":[2.0,0.0,2.33,1.0],
    "1B":[9.46,7.78,0.0,0.0],
    "2B":[7.92,14.06,0.0,0.0],
    "3B":[15.25,14.22,0.0,0.0],
    "SS":[6.83,19.61,0.0,0.0],
    "LF":[15.46,5.94,5.17,0.0],
    "CF":[15.46,6.39,8.0,0.0],
    "RF":[15.75,6.44,6.83,0.0],
    "DH":[0.0,0.0,0.0,0.0]
}

def process(year):
    if year <= 2016:
        register_war(year)
    else:
        statistics_war(year)

    # for year in range(2006,2017):
    #     register_war(year)


def get_hand(player_name):
    if player_name[len(player_name)-1:] == "*":
        hand = 'l'
    elif player_name[len(player_name)-1:] == "#":
        hand = 's'
    else:
        hand = 'r'

    return hand


def get_def_values(search_name, position, year):
    p = position.lower()
    pos = position.upper()
    rn = '%s_range' % p
    er = '%s_error' % p
    arm, pb = 0,2
    if p == 'c':
        arm = 'c_arm'
        pb = 'c_pb'
    elif p in ('lf','rf','cf'):
        arm = 'of_arm'

    try:
        if p not in ('p','dh'):
            rtg_q = """SELECT
%s,
%s,
%s,
%s
FROM zips_defense_%s
WHERE player_name = '%s'"""
        
            rtg_qry = rtg_q % (rn, er, arm, pb, year, search_name)
            rtgs = db.query(rtg_qry)[0]
        else:
            rtgs = (0,0,0,0)
    except IndexError:
        rtgs = (0,0,0,0)

    _r, error, _a, passed_ball = rtgs
    if error is None:
        error = 100
    if _r is None:
        _r = 'AV'
    if _a is None:
        _a = 'AV'
    if passed_ball is None:
        passed_ball = 2
    _range = str(_r)
    _arm = str(_a)

    # range and arm text values need to translate to numeric values
    if _range.upper() in ('PO','PR'):
        num_rn = -2
    elif _range.upper() in ('FR',):
        num_rn = -1
    elif _range.upper() in ('AV','AVG'):
        num_rn = 0
    elif _range.upper() in ('VG',):
        num_rn = 1
    elif _range.upper() in ('EX',):
        num_rn = 2
    else:
        num_rn = 0

    if _arm.upper() in ('PO','PR'):
        num_arm = -2
    elif _arm.upper() in ('FR',):
        num_arm = -1
    elif _arm.upper() in ('AV','AVG'):
        num_arm = 0
    elif _arm.upper() in ('VG',):
        num_arm = 1
    elif _arm.upper() in ('EX',):
        num_arm = 2
    else:
        num_arm = 0

    weights = pos_formula.get(pos)

    rn_val = weights[0]*num_rn
    #100 is average error rating. we want the amount above/below this number
    err_val = weights[1]*((100-float(error))/100)
    arm_val = weights[2]*num_arm
    pb_val = weights[3]*(2-passed_ball)

    return rn_val, err_val, arm_val, pb_val



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

        bats = get_hand(player_name)
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

            pos = position.upper()
            adj = float(pos_adj.get(pos))
            position_adj = adj*(pa/700)
            entry['position_adj'] = position_adj

        else:
            # changes Travis d'Arnoud to Travis d''Arnoud
            search_name = s_name.replace("'","''")
            rn_val, err_val, arm_val, pb_val = get_def_values(search_name, position, year)

            #700 pa is a full season
            defense = float(pa)*(rn_val + err_val + arm_val + pb_val)/700

            entry['defense'] = defense
            adj = float(pos_adj.get(position.upper()))
            position_adj = adj*(float(pa)/700)
            entry['position_adj'] = position_adj
            

        dwar = (defense+position_adj)/10.0

        entry['dWAR'] = dwar

        entries.append(entry)


    table = 'processed_compWAR_defensive'
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()


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

            rn_val, err_val, arm_val, pb_val = get_def_values(search_name, position, year)

            #1450 innings is a full season
            defense = float(inn)*(rn_val + err_val + arm_val + pb_val)/1450

            entry['defense'] = defense
            adj = float(pos_adj.get(position.upper()))
            position_adj = adj*(float(inn)/1450)
            entry['position_adj'] = position_adj

            dwar = (defense+position_adj)/10

            entry['dWAR'] = dwar

            entries.append(entry)


    table = 'processed_compWAR_defensive'
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()



if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process(args.year)
    