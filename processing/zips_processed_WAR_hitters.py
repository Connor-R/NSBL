from py_db import db
import argparse
from decimal import Decimal


# Goes through the list of projected offensive players, and cycles through all 9 positions (including DH). if the position exists, it writes a row. if not, it doesn't.


db = db('NSBL')
park_factors = {
    "ANA":98.33,
    "LAA":98.33,
    "HOU":98.33,
    "OAK":100,
    "TOR":99,
    "ATL":99.67,
    "MIL":101,
    "STL":99.33,
    "CHC":100.67,
    "CHN":100.67,
    "ARI":101.33,
    "AZ":101.33,
    "AZD":101.33,
    "LA":98.67,
    "LAD":98.67,
    "LAN":98.67,
    "SF":97.67,
    "SFG":97.67,
    "CLE":99,
    "CLV":99,
    "SEA":99,
    "FLA":100.33,
    "FLO":100.33,
    "MIA":100.33,
    "NYM":98.33,
    "NYN":98.33,
    "WAN":100,
    "WAS":100,
    "BAL":100.67,
    "BALT":100.67,
    "SAN":98,
    "SD":98,
    "SDP":98,
    "PHI":100,
    "PIT":99,
    "TEX":102,
    "TAM":98.33,
    "TB":98.33,
    "TBA":98.33,
    "TBR":98.33,
    "BOS":101.33,
    "CIN":100.33,
    "COL":105.67,
    "KC":100.33,
    "KCR":100.33,
    "DET":100.67,
    "MIN":100.33,
    "CHA":101.33,
    "CHW":101.33,
    "CWS":101.33,
    "NYA":101,
    "NYY":101,
    "NONE":100,
    "":100,
}

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
    calculate_war(year)

    # for year in range(2011,2017):
    #     calculate_war(year)

def get_league_avg(year, category):
    yr = year-1
    q = """SELECT
pa,
r,
(h+bb+hbp)/pa as obp,
(1b + 2*2b + 3*3b + 4*hr)/ab as slg,
woba
FROM processed_league_averages_hitting
WHERE year = %s
"""
    qry = q % yr
    query = db.query(qry)[0]
    lg_pa, lg_r, lg_obp, lg_slg, lg_woba = query
    avgs = {"lg_pa":lg_pa, "lg_r":lg_r, "lg_obp":lg_obp, "lg_slg":lg_slg, "lg_woba":lg_woba}

    return avgs.get(category)



def get_zips_def_ratings(search_name, position, year):
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

    if rtgs[:2] == ('', None):
        rn_val, err_val, arm_val, pb_val = None, None, None, None

    else:
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



def calculate_war(year):
    player_q = """SELECT
*
FROM zips_offense_%s
"""
    player_qry = player_q % (year)
    player_list = db.query(player_qry)

    entries = []
    for row in player_list:
        player_name, team_abb, g, ab, r, h, _2b, _3b, hr, rbi, bb, so, hbp, sb, cs, sh, sf, ibb = row

        _1b = h-_2b-_3b-hr
        pa = ab+bb+hbp+sh+sf

        team_abb = team_abb.upper()
        pf = float(park_factors.get(team_abb))/float(100)
        
        wOBA = ((0.691*bb + 0.722*hbp + 0.884*_1b + 1.257*_2b + 1.593*_3b + 2.058*hr + 0.2*sb - 0.398*cs)/(pa))
        
        park_wOBA = wOBA/pf 

        lg_woba = float(get_league_avg(year,'lg_woba'))

        # offensive runs added per 600 PA
        raa = 600*((park_wOBA-lg_woba)/1.25)

        oWAR = raa/10

        for pos in ('c','1b','2b','3b','ss','lf','rf','cf','dh'):
            search_name = player_name.replace("'","''")


            rn_val, err_val, arm_val, pb_val = get_zips_def_ratings(search_name, pos, year)

            if rn_val == None and err_val == None and arm_val == None and pb_val == None:
                continue

            else:

                #defensive runs added per 600 pa
                defense = 600*(rn_val + err_val + arm_val + pb_val)/700

                position_adj = float(pos_adj.get(pos.upper()))
               

                dWAR = (defense+position_adj)/10.0

                replacement = 20.0

                entry = {}
                entry['player_name'] = player_name
                entry['team_abb'] = team_abb
                entry['position'] = pos
                entry['pf'] = pf
                entry['position_adj'] = position_adj
                entry['defense'] = defense
                entry['dWAR'] = dWAR
                entry['park_wOBA'] = park_wOBA
                entry['rAA'] = raa
                entry['oWAR'] = oWAR

                war = (replacement+raa+defense+position_adj)/10.0

                entry['WAR'] = war

                entries.append(entry)


    table = 'zips_processed_WAR_hitters_%s' % year
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()



if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process(args.year)
    