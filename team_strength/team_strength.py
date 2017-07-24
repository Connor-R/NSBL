from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import numpy as np

# script that estiamtes overall team strength by comparing in-season performance to optimized roster strength (lineup vsL, lineup vsR, starting rotation, bullpen) <-- need to add in bench strength


db = db('NSBL')


def process():
    start_time = time()

    #Each time we run this, we clear the pre-existing table
    db.query("TRUNCATE TABLE `__team_strength`")

    get_optimal_lineups()

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "pitching_optimizer.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def get_optimal_lineups():
    optimal_query = """SELECT team_abb, 
    total_val AS pitching_val, starter_val, reliever_val, 
    l.lineup_val AS lineup_vsL, r.lineup_val AS lineup_vsR,
    total_val + 0.75*(l.lineup_val) + 0.25*(r.lineup_val) AS roster_WAR
    FROM __optimal_pitching p
    JOIN __optimal_lineups l USING (team_abb)
    JOIN __optimal_lineups r USING (team_abb)
    WHERE l.vs_hand = 'l'
    AND r.vs_hand = 'r'
    AND l.dh_name IS NOT NULL
    AND r.dh_name IS NOT NULL
    ORDER BY team_abb DESC;"""

    optimal_res = db.query(optimal_query)

    for row in optimal_res:
        entry = {}
        team_abb, pitching_val, starter_val, reliever_val, lu_vsL, lu_vsR, roster_WAR = row

        rep_team_win_pct = 0.25
        roster_W = float(roster_WAR) + rep_team_win_pct*162
        roster_pct = roster_W/162.0

        mascot_name = helper.get_mascot_names(team_abb.upper())

        team_name, rep_WAR, oWAR, dWAR, FIP_WAR, W, L = get_standing_metrics(mascot_name)

        current_g = float(W+L)
        w_pct = float(W)/float(W+L)

        ros_g = 162-current_g
        ros_pct = (roster_pct + (current_g/162.0)*w_pct)/(1 + (current_g/162.0))

        ros_W = ros_pct*ros_g

        projected_W = W + ros_W
        projected_pct = projected_W/162.0

        entry['team_abb'] = team_abb
        entry['roster_strength'] = roster_WAR
        entry['roster_W'] = roster_W
        entry['roster_L'] = 162.0 - roster_W
        entry['roster_pct'] = roster_pct
        entry['current_W'] = W
        entry['current_L'] = L
        entry['current_pct'] = w_pct
        entry['ros_W'] = ros_W
        entry['ros_L'] = ros_g - ros_W
        entry['ros_pct'] = ros_pct
        entry['projected_W'] = projected_W
        entry['projected_L'] = 162.0 - projected_W
        entry['projected_pct'] = projected_pct

        db.insertRowDict(entry, '__team_strength', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()


def get_standing_metrics(mascot_name):
    qry = """SELECT 
team_name, repWAR, oWAR, dWAR, FIP_WAR, W, L 
FROM processed_team_standings_advanced
WHERE year = 2017
AND team_name LIKE '%%%s%%'"""

    query = qry % (mascot_name)

    return db.query(query)[0]


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process()
    