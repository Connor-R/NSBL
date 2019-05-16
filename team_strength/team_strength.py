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
    starter_var, bullpen_var,
    l.lineup_var AS vsL_var, r.lineup_var AS vsR_var,
    total_var + 0.25*l.lineup_var + 0.75*r.lineup_var AS roster_var
    FROM __optimal_pitching p
    JOIN __optimal_lineups l USING (team_abb)
    JOIN __optimal_lineups r USING (team_abb)
    WHERE l.vs_hand = 'l'
    AND r.vs_hand = 'r'
    AND l.dh_name IS NOT NULL
    AND r.dh_name IS NOT NULL
    ORDER BY team_abb ASC;"""

    total_roster_war_query = """SELECT
    SUM(p.total_val + 0.25*(l.lineup_val) + 0.75*(r.lineup_val)) AS roster_WAR
    FROM __optimal_pitching p
    JOIN __optimal_lineups l USING (team_abb)
    JOIN __optimal_lineups r USING (team_abb)
    WHERE l.vs_hand = 'l'
    AND r.vs_hand = 'r'
    AND l.dh_name IS NOT NULL
    AND r.dh_name IS NOT NULL;"""

    total_roster_war = db.query(total_roster_war_query)[0][0]

    replacement_team_wins = (2430-float(total_roster_war))/30
    rep_team_win_pct = float(replacement_team_wins)/162

    optimal_res = db.query(optimal_query)

    for row in optimal_res:
        entry = {}
        team_abb, starter_val, bullpen_val, lu_vsL, lu_vsR, roster_WAR, starter_var, bullpen_var, vsL_var, vsR_var, roster_var = row

        mascot_name = helper.get_mascot_names(team_abb.upper())

        team_name, games_played, rep_WAR, oWAR, dWAR, FIP_WAR, W, L, py_W, py_L = get_standing_metrics(year, mascot_name)

        games_played = float(games_played)

        if games_played > 162.0:
            roster_W = float(roster_WAR) + rep_team_win_pct*games_played
            roster_pct = roster_W/games_played
            ros_g = 0
        else:
            roster_W = float(roster_WAR) + rep_team_win_pct*162
            roster_pct = roster_W/162.0
            ros_g = 162-games_played

        try:
            w_pct = float(W)/float(W+L)
            py_pct = float(py_W)/float(py_W+py_L)
        except ZeroDivisionError:
            w_pct = 0.5
            py_pct = 0.5



        # weighted geometric mean (regressed towards roster strength)
        # (roster%^(remaining_games+80) * pythag%^((played_games+4)/2) * win%^((played_games+4)/2))^(1/250)
        ros_pct = ( (roster_pct**(ros_g+80)) * (max(py_pct,0.25)**(float(games_played+4.0)/2.0)) * (max(w_pct,0.25)**(float(games_played+4.0)/2.0)) ) ** (1.0/250.0)
        if team_abb == 'Pit':
            print roster_pct, ros_g, py_pct, games_played, w_pct
            raw_input(row)
            raw_input(ros_pct)

        ros_W = ros_pct*ros_g


        # for the total amount of variance for the team, we first take the total amount of variance from team projections (based on the variance in each individual player's projection)
        total_roster_var = float(roster_var) 
        # then we add a measure of variance based on the difference between true talent record (pythag record) and observed record (see /variance_research/Full Season Pythag Standings Variance research.png)
        total_roster_var += -0.0052542947*(ros_pct*162) + 3.4279721907
        # Finally we add a value of 5.0 to the STANDARD DEVIATION (not variance). We can express the amount of variance desired to add in the set of equations {std = sqrt(v), std+5.0 = sqrt(v+c)}, and then solving for c (https://tinyurl.com/y8tk64ez)
        # NB. the value of 5.0 is a guess (~0.33 win for each starter plus a small amount for bench players and relief pitchers) and hack-y and should be cleaned up, or at least weighted more towards defensive #s over wOBA numbers) wins to the variance due to my uncertain nature (mostly from defense) of my conversion from raw ZiPS to DMB WAR (i.e., I think if my projection says the team is a true talent 90 win team, I think there is +/- 5.0 wins of standard deviation in that projection)
        total_roster_var += 10*math.sqrt(total_roster_var) + 25

        



        projected_W = W + ros_W
        

        if games_played > 162.0:
            roster_L = games_played - roster_W
            projected_L = games_played - projected_W
            projected_pct = projected_W/games_played
        else:
            roster_L = 162.0 - roster_W
            projected_L = 162.0 - projected_W
            projected_pct = projected_W/162.0

        entry['team_abb'] = team_abb
        entry['team_name'] = team_name
        entry['year'] = year
        entry['games_played'] = games_played
        entry['starter_val'] = starter_val
        entry['bullpen_val'] = bullpen_val
        entry['vsR_val'] = lu_vsR
        entry['vsL_val'] = lu_vsL
        entry['roster_strength'] = roster_WAR
        entry['starter_var'] = starter_var
        entry['bullpen_var'] = bullpen_var
        entry['vsR_var'] = vsR_var
        entry['vsL_var'] = vsL_var
        entry['roster_var'] = roster_var
        entry['overall_var'] = total_roster_var    
        entry['roster_W'] = roster_W
        entry['roster_L'] = roster_L
        entry['roster_pct'] = roster_pct
        entry['current_W'] = W
        entry['current_L'] = L
        entry['current_pct'] = w_pct
        entry['ros_W'] = ros_W
        entry['ros_L'] = ros_g - ros_W
        entry['ros_pct'] = ros_pct
        entry['projected_W'] = projected_W
        entry['projected_L'] = projected_L
        entry['projected_pct'] = projected_pct

        # raw_input(entry)
        db.insertRowDict(entry, '__team_strength', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()


def get_standing_metrics(year, mascot_name):
    qry = """SELECT 
    team_name, games_played, repWAR, oWAR, dWAR, FIP_WAR, W, L, py_Wins, py_Losses
    FROM processed_team_standings_advanced
    WHERE year = %s
    AND team_name LIKE '%%%s%%'
    AND games_played = (SELECT MAX(games_played) FROM processed_team_standings_advanced WHERE year = %s AND team_name LIKE '%%%s%%');"""

    query = qry % (year, mascot_name, year, mascot_name)
    # raw_input(query)

    return db.query(query)[0]

    # return db.query(query)[0][0], 0,0,0,0,0,0,0,0,0


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2019)
    args = parser.parse_args()
    
    process(args.year)
    

