from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import math
import numpy as np

# script that estiamtes overall team strength by comparing in-season performance to optimized roster strength (lineup vsL, lineup vsR, starting rotation, bullpen) <-- need to add in bench strength


db = db('NSBL')


def process(year):
    start_time = time()

    get_optimal_lineups(year)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "team_strength.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def get_optimal_lineups(year):
    optimal_query = """SELECT team_abb, 
    starter_val, bullpen_val, 
    l.lineup_val AS lineup_vsL, r.lineup_val AS lineup_vsR,
    total_val + 0.25*(l.lineup_val) + 0.75*(r.lineup_val) AS roster_WAR,
    starter_std, bullpen_std,
    l.lineup_std AS vsL_std, r.lineup_std AS vsR_std,
    POWER(total_std,2) + 0.25*(POWER(l.lineup_std,2)) + 0.75*(POWER(r.lineup_std,2)) AS roster_std
    FROM __optimal_pitching p
    JOIN __optimal_lineups l USING (team_abb)
    JOIN __optimal_lineups r USING (team_abb)
    WHERE l.vs_hand = 'l'
    AND r.vs_hand = 'r'
    AND l.dh_name IS NOT NULL
    AND r.dh_name IS NOT NULL
    ORDER BY team_abb ASC;"""

    optimal_res = db.query(optimal_query)

    for row in optimal_res:
        entry = {}
        team_abb, starter_val, bullpen_val, lu_vsL, lu_vsR, roster_WAR, starter_std, bullpen_std, vsL_std, vsR_std, roster_std = row

        roster_std = math.sqrt(roster_std)

        rep_team_win_pct = 0.25
        roster_W = float(roster_WAR) + rep_team_win_pct*162
        roster_pct = roster_W/162.0

        mascot_name = helper.get_mascot_names(team_abb.upper())

        team_name, rep_WAR, oWAR, dWAR, FIP_WAR, W, L, py_W, py_L = get_standing_metrics(year, mascot_name)

        current_g = float(W+L)
        w_pct = float(W)/float(W+L)

        py_pct = float(py_W)/float(py_W+py_L)

        # current_g = 162
        ros_g = 162-current_g
        # weighted geometric mean (regressed towards roster strength)
        # (roster%^(remaining_games+80) * pythag%^((played_games+4)/2) * win%^((played_games+4)/2))^(1/250)
        ros_pct = ( (roster_pct**(ros_g+80)) * (max(py_pct,0.001)**(float(current_g+4.0)/2.0)) * (max(w_pct,0.001)**(float(current_g+4.0)/2.0)) ) ** (1.0/250.0)

        # weighted arithmetic mean
        # ros_pct = (roster_pct + (current_g/162.0)*w_pct)/(1 + (current_g/162.0))

        ros_W = ros_pct*ros_g

        projected_W = W + ros_W
        projected_pct = projected_W/162.0

        entry['team_abb'] = team_abb
        entry['team_name'] = team_name
        entry['year'] = year
        entry['games_played'] = current_g
        entry['starter_val'] = starter_val
        entry['bullpen_val'] = bullpen_val
        entry['vsR_val'] = lu_vsR
        entry['vsL_val'] = lu_vsL
        entry['roster_strength'] = roster_WAR
        entry['starter_std'] = starter_std
        entry['bullpen_std'] = bullpen_std
        entry['vsR_std'] = vsR_std
        entry['vsL_std'] = vsL_std
        entry['roster_std'] = roster_std    
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

        # raw_input(entry)
        db.insertRowDict(entry, '__team_strength', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()


def get_standing_metrics(year, mascot_name):
    qry = """SELECT 
team_name, repWAR, oWAR, dWAR, FIP_WAR, W, L, py_Wins, py_Losses
FROM processed_team_standings_advanced
WHERE year = %s
AND team_name LIKE '%%%s%%'"""

    query = qry % (year, mascot_name)

    return db.query(query)[0]


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process(args.year)
    