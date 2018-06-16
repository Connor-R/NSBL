from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time


# Goes through the list of projected offensive players, and cycles through all 9 positions (including DH). if the position exists, it writes a row. if not, it doesn't.


db = db('NSBL')


def process():
    start_time = time()

    calculate_war()

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "zips_WAR_hitters.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def calculate_war():
    player_q = """SELECT
    year, player_name, team_abb, age, bats, 
    ab, h, 2b, 3b, hr, bb, so, hbp, ibb, sh, sf, sb, cs
    FROM zips_offense
    """
    player_qry = player_q
    player_list = db.query(player_qry)

    entries = []
    for row in player_list:
        year, player_name, team_abb, age, bats, ab, h, _2, _3, hr, bb, so, hbp, ibb, sh, sf, sb, cs = row
        print year, player_name

        _1 = h-_2-_3-hr
        pa = ab+bb+hbp+ibb+sh+sf
        bb2 = bb+ibb

        team_abb = team_abb.upper()
        pf = float(helper.get_park_factors(team_abb))/float(100)

        ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR = helper.get_zips_offensive_metrics(year-1, pf, pa, ab, bb2, hbp, _1, _2, _3, hr, sb, cs)

        oWAR = (oWAR/float(pa))*float(600)

        if year >= 2014:
            vsL_wRC_plus, vsL_oWAR = get_split_offense(year, player_name, 'L')
            vsR_wRC_plus, vsR_oWAR = get_split_offense(year, player_name, 'R')
        else:
            vsL_wRC_plus = None
            vsR_wRC_plus = None
            vsL_oWAR = None
            vsR_oWAR = None

        for pos in ('c','1b','2b','3b','ss','lf','rf','cf','dh'):
            search_name = player_name.replace("'","''").replace("!","").replace("?","")


            rn_val, err_val, arm_val, pb_val, _range, error, _arm, passed_ball = get_zips_def_ratings(search_name, pos, year)

            if rn_val == None and err_val == None and arm_val == None and pb_val == None:
                continue

            else:

                #defensive runs added per 600 pa
                defense = 600*(rn_val + err_val + arm_val + pb_val)/700

                position_adj = float(helper.get_pos_adj(pos.upper()))

                dWAR = (defense+position_adj)/10.0

                replacement = 20.0

                vsL_WAR = None
                vsR_WAR = None
                if vsL_oWAR is not None:
                    vsL_WAR = 2.0+dWAR+vsL_oWAR
                if vsR_oWAR is not None:
                    vsR_WAR = 2.0+dWAR+vsR_oWAR

                WAR = 2.0+dWAR+oWAR

                if pos != 'c':
                    passed_ball = None

                if pos not in ('c', 'lf', 'cf', 'rf'):
                    _arm = None

                if pos == 'dh':
                    _range, error = None, None

                entry = {}
                entry['year'] = year
                entry['player_name'] = player_name
                entry['team_abb'] = team_abb
                entry['age'] = age
                entry['position'] = pos
                entry['bats'] = bats
                entry['pf'] = pf
                entry['position_adj'] = position_adj
                entry['rn'] = _range
                entry['er'] = error
                entry['arm'] = _arm
                entry['pb'] = passed_ball
                entry['DRS'] = defense
                entry['dWAR'] = dWAR
                entry['vsL_wRC_plus'] = vsL_wRC_plus
                entry['vsR_wRC_plus'] = vsR_wRC_plus
                entry['wRC_plus'] = wRC_plus
                entry['vsL_oWAR'] = vsL_oWAR
                entry['vsR_oWAR'] = vsR_oWAR
                entry['oWAR'] = oWAR
                entry['vsL_WAR'] = vsL_WAR
                entry['vsR_WAR'] = vsR_WAR
                entry['WAR'] = WAR

                # raw_input(entry)

                entries.append(entry)


    table = 'zips_WAR_hitters'
    print table
    if entries != []: 
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i:i+1000], table, replace=True, insertMany=True, rid=0)
        db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


def get_split_offense(year, player_name, vs_hand):
    player_name = player_name.replace("'","''")

    vs_q = """SELECT
    year, player_name, team_abb,
    o1.ab, o1.h, o1.2b, o1.3b, o1.hr, o1.bb, o1.so, o1.hbp, o1.ibb, o1.sh, o1.sf
    FROM zips_offense_splits o1
    JOIN zips_offense o2 USING (player_name, year)
    WHERE vs_hand = '%s'
    AND year = %s
    AND player_name = '%s'
    """
    vs_qry = vs_q % (vs_hand, year, player_name)

    try:
        vs_stats = db.query(vs_qry)[0]
    except IndexError:
        return None, None

    year, player_name, team_abb, ab, h, _2, _3, hr, bb, so, hbp, ibb, sh, sf = vs_stats

    _1 = h-_2-_3-hr
    pa = ab+bb+hbp+ibb+sh+sf
    bb2 = bb+ibb

    team_abb = team_abb.upper()
    pf = float(helper.get_park_factors(team_abb))/float(100)

    ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR = helper.get_zips_offensive_metrics(year-1, pf, pa, ab, bb2, hbp, _1, _2, _3, hr, 0, 0)

    vs_wRC_plus = wRC_plus
    vs_oWAR = (oWAR/float(pa))*float(600)

    return vs_wRC_plus, vs_oWAR


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
    FROM zips_defense
    WHERE player_name = '%s'
    AND year = %s"""
        
            rtg_qry = rtg_q % (rn, er, arm, pb, search_name, year)
            rtgs = db.query(rtg_qry)[0]
        else:
            rtgs = (0,0,0,0)
    except IndexError:
        rtgs = (0,0,0,0)

    if rtgs[:2] == (None, None):
        rn_val, err_val, arm_val, pb_val, _range, error, _arm, passed_ball  = None, None, None, None, None, None, None, None

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

        weights = helper.get_pos_formula(pos)

        rn_val = weights[0]*num_rn
        #100 is average error rating. we want the amount above/below this number
        err_val = weights[1]*((100-float(error))/100)
        arm_val = weights[2]*num_arm
        pb_val = weights[3]*(2-passed_ball)

    return rn_val, err_val, arm_val, pb_val, _range, error, _arm, passed_ball


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2018)
    args = parser.parse_args()
    
    process()
    

