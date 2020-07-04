from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time


# Goes through the list of projected pitchers and projects their split pitching WAR components


db = db('NSBL')


def process():
    start_time = time()

    calculate_war()

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "zips_WAR_pitchers_comp.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def calculate_war():
    player_q = """SELECT
    year,
    player_name,
    team_abb,
    vs_hand,
    ps.ab, ps.h, ps.2b, ps.3b, ps.hr, ps.bb, ps.so, ps.hbp, ps.ibb, ps.sh, ps.sf
    FROM zips_pitching_splits ps
    JOIN zips_pitching USING (year, player_name)
    """
    player_qry = player_q
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        year, player_name, team_abb, vs_h, ab, h, _2, _3, hr, bb, so, hbp, ibb, sh, sf = row

        pa = ab+bb+hbp+ibb+sh+sf
        bb2 = bb+ibb
        _1 = h - _2 - _3 - hr

        team_abb = team_abb.upper()
        pf = float(helper.get_park_factors(team_abb, year-1))/float(100)

        babip = float((h-hr))/float((ab+sh+sf-so-hr))

        ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR = helper.get_zips_offensive_metrics(year-1, pf, pa, ab, bb2, hbp, _1, _2, _3, hr, 0, 0)

        entry['year'] = year
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['vs_hand'] = vs_h
        entry['pf'] = pf
        entry['pa'] = pa
        entry['babip'] = babip
        entry['OPS_plus_against'] = OPS_plus
        entry['park_wOBA_against'] = park_wOBA
        entry['wRC_plus_against'] = wRC_plus

        entries.append(entry)


    table = 'zips_WAR_pitchers_comp'
    if entries != []:
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i: i + 1000], table, insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2018)
    args = parser.parse_args()
    
    process()


