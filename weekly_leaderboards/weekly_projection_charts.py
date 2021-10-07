from py_db import db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import NSBL_helpers as helper
import os
from time import time


# Plotting my weekly projections for each team


db = db('NSBL')

path = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/i/NSBL_WeeklyProjections/"

desired_font = "Trajan Pro"
plt.rc('font', family=desired_font)

def initiate(year):
    start_time = time()
    print "\nWeekly Charts"


    print '\t', year, 'NSBL Team Wins'
    plot_all(year, 'Wins')

    print '\t', year, 'NSBL Team Playoff Odds'    
    plot_all(year, 'Playoff Odds')

    print '\t', year, 'NSBL Team World Series Odds'    
    plot_all(year, 'World Series Odds')

    teams = db.query("select distinct(team_name) from __playoff_probabilities where year =" + str(year) + ";")

    for t in teams:
        team_name = t[0]
        print '\t', year, team_name

        plot_team(year, team_name)



    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nweekly_projection_charts.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def plot_team(year, team_name):
    qry = """SELECT 
    team_name, team_abb, games_played, current_W, mean_W, (162*strength_pct) as 'team_strength', (win_division+wc_1+wc_2) as 'make_playoffs', win_division, make_ws, win_ws
    FROM __playoff_probabilities
    JOIN __team_strength USING (team_name, team_abb, games_played, year)
    WHERE strength_type = "projected"
    AND win_ws IS NOT NULL
    AND wc_1 IS NOT NULL
    AND wc_2 IS NOT NULL
    AND win_division IS NOT NULL
    AND year = %s
    AND team_name = "%s"
    ORDER BY games_played ASC;"""

    query = qry % (year, team_name)
    res = db.query(query)

    games_list = []
    wins_list = []
    xWins_list = []
    strength_list = []
    xWeekly_list = []
    playoffs_list = []
    division_list = []
    pennant_list = []
    ws_list = []

    temp_games = 0
    temp_wins = 0 
    for row in res:
        foo, team_abb, games_played, wins, expected_wins, team_strength, make_playoffs, win_division, win_pennant, win_ws = row

        week_games = games_played - temp_games
        week_wins = (float(expected_wins)/162.0)*float(week_games) + float(temp_wins)

        games_list.append(int(games_played))
        wins_list.append(float(wins))
        xWins_list.append(float(expected_wins))
        strength_list.append(float(team_strength))
        xWeekly_list.append(float(week_wins))
        playoffs_list.append(float(make_playoffs))
        division_list.append(float(win_division))
        pennant_list.append(float(win_pennant))
        ws_list.append(float(win_ws))

        temp_games += week_games
        temp_wins = week_wins

    post_qry = """SELECT 
    make_ws, win_ws
    FROM __in_playoff_probabilities
    WHERE strength_type = "projected"
    AND win_ws IS NOT NULL
    AND year = %s
    AND team_name = "%s"
    ORDER BY total_playoff_games_played ASC;"""


    post_query = post_qry % (year, team_name)
    res = db.query(post_query)

    for playoff_cnt, row in enumerate(res):
        win_pennant, win_ws = row
        games_list.append(int(games_played+playoff_cnt))
        wins_list.append(None)
        xWins_list.append(None)
        strength_list.append(None)
        xWeekly_list.append(None)
        playoffs_list.append(None)
        division_list.append(None)
        pennant_list.append(float(win_pennant))
        ws_list.append(float(win_ws))

        if win_ws == 0:
            break    

    x = np.array(games_list)
    y1 = np.array(wins_list)
    y2 = np.array(xWins_list)
    y2b = np.array(xWeekly_list)
    y2c = np.array(strength_list)
    y3 = np.array(playoffs_list)
    y4 = np.array(division_list)
    y4b = np.array(pennant_list)
    y5 = np.array(ws_list)

    figtit = path + str(year) + '_' + team_abb.upper() + '-WeeklyProjections' + '.png'


    fig = plt.figure(figsize=(10,10))
    
    ax1 = plt.axes([0.08, 0.08, 0.84, 0.775]) 
    plt.grid()


    plt.title(str(year) + ' - ' + team_name + ' - Weekly Projections', fontsize = 20, y=1.125)

    ax1.scatter(x, y1, s=20, color='r')
    ln1 = ax1.plot(x, y1, linewidth=2, linestyle='-', label='Observed Wins', color='r')

    ax1.scatter(x, y2b, s=20, color='orange')   
    ln2b = ax1.plot(x, y2b, linewidth=2, linestyle='-', label='Projected Wins', color='orange')

    ax1.scatter(x, y2c, s=20, color='slategray')   
    ln2c = ax1.plot(x, y2c, linewidth=2, linestyle='-', label='Team Strength Wins', color='slategray')

    ax1.scatter(x, y2, s=20, color='black')   
    ln2 = ax1.plot(x, y2, linewidth=2, linestyle='-', label='End of Season Projected Wins', color='black')


    ax1.set_xlabel('Games Played')
    ax1.set_ylabel('Wins')
    ax1.set_ylim([-0.6,120.6])
    ax1.set_xlim([-0.01,180.75])
    ax1.set_yticks(np.arange(0, 121, 6.0))
    ax1.set_xticks(np.arange(0, 181, 10))
    ax1.tick_params('n')

    for label in ax1.get_xticklabels():
        label.set_fontproperties(desired_font)
    for label in ax1.get_yticklabels():
        label.set_fontproperties(desired_font)

    ax2 = ax1.twinx()
    ax2.scatter(x, y3, s=10, color='b')
    ln3 = ax2.plot(x, y3, linewidth=1, linestyle='-', label='Make Playoffs', color='b')

    ax2.scatter(x, y4, s=10, color='m')
    ln4 = ax2.plot(x, y4, linewidth=1, linestyle='-', label='Win Division', color='m')

    ax2.scatter(x, y4b, s=10, color='g')
    ln4b = ax2.plot(x, y4b, linewidth=1, linestyle='-', label='Win Pennant', color='g')

    ax2.scatter(x, y5, s=10, color='c')
    ln5 = ax2.plot(x, y5, linewidth=1, linestyle='-', label='Win World Series', color='c')

    if (year == 2018 and team_name in ('Cleveland Indians', 'Seattle Mariners')):
        reg_games = 163
    else:
        reg_games = 162

    ln6 = ax2.plot([reg_games,reg_games], [0,1], alpha=0.5, linewidth=1, linestyle='--', label='End of Regular Season', color='y', zorder=1)


    ax2.set_xlabel('Games Played')
    ax2.set_ylabel('Probability')
    ax2.set_ylim([-0.005,1.005])
    ax2.set_yticks(np.arange(0, 1.005, .1))
    ax2.tick_params('n')

    for label in ax2.get_xticklabels():
        label.set_fontproperties(desired_font)
    for label in ax2.get_yticklabels():
        label.set_fontproperties(desired_font)    


    lns = ln1+ln2b+ln2c+ln2+ln3+ln4+ln4b+ln5
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, bbox_to_anchor=(0., 1.0001, 1., .105), loc='lower left', ncol=2, mode="expand")

    plt.savefig(figtit)
    plt.close()



def plot_all(year, plot_type):

    if plot_type == "Wins":
        qry_add = "mean_W"
    elif plot_type == "Playoff Odds":
        qry_add = "(win_division+wc_1+wc_2)"
    elif plot_type == "World Series Odds":
        qry_add = "win_ws"

    fig = plt.figure(figsize=(10,10))
    
    ax1 = plt.axes([0.08, 0.08, 0.80, 0.85]) 
    plt.grid()

    figtit = path + str(year) + '_NSBL_' + plot_type.replace(' ','') + '-WeeklyProjections' + '.png'

    plt.title(str(year) + ' - ' + plot_type + ' - Weekly Projections', fontsize = 20)

    teams = db.query("select distinct(team_name) from __playoff_probabilities where year =" + str(year) + ";")
    
    for i, t in enumerate(teams):
        team_name = t[0]

        t_qry = """SELECT 
        team_abb, games_played, 
        %s
        FROM __playoff_probabilities
        WHERE strength_type = "projected"
        AND win_ws IS NOT NULL
        AND wc_1 IS NOT NULL
        AND wc_2 IS NOT NULL
        AND win_division IS NOT NULL
        AND year = %s
        AND team_name = "%s"
        ORDER BY games_played ASC;"""

        t_query = t_qry % (qry_add, year, team_name)
        # raw_input(t_query)

        x_list = []
        y_list = []
        res = db.query(t_query)

        for row in res:
            list_label, x_val, y_val = row

            x_list.append(x_val)
            y_list.append(y_val)

        if plot_type == "World Series Odds":
            post_qry = """SELECT 
            team_abb, %s
            FROM __in_playoff_probabilities
            WHERE strength_type = "projected"
            AND win_ws IS NOT NULL
            AND year = %s
            AND team_name = "%s"
            ORDER BY total_playoff_games_played ASC;"""

            post_query = post_qry % (qry_add, year, team_name)
            res = db.query(post_query)

            for playoff_cnt, row in enumerate(res):
                team_abb, playoff_val = row

                x_list.append(int(163+playoff_cnt))
                y_list.append(playoff_val)

                if playoff_val == 0:
                    break
     

        x = np.array(x_list)
        y = np.array(y_list)

        ax1.scatter(x, y, s=10)

        if int(i/10) == 0:
            linestyle =  '-'
        elif int(i/10) == 1:
            linestyle = '--'
        elif int(i/10) == 2:
            linestyle = '-.'

        ax1.plot(x, y, linewidth=1, linestyle=linestyle, label=list_label.upper())

        ax1.set_xlabel('Games Played')
        ax1.set_ylabel(plot_type)
        ax1.tick_params('n')

        for label in ax1.get_xticklabels():
            label.set_fontproperties(desired_font)
        for label in ax1.get_yticklabels():
            label.set_fontproperties(desired_font)

    if plot_type == "World Series Odds":
        if max(x_list) > 162:

            if (year == 2018):
                reg_games = 163
            else:
                reg_games = 162

            ln6 = ax1.plot([reg_games,reg_games], [0,1], alpha=0.5, linewidth=0.8, linestyle=':', label='Post\nSeason', color='r', zorder=1)
   
    if plot_type != "Wins":
        ax1.set_ylim([-0.005,1.005])
        plt.yticks(np.arange(0.00, 1.005, 0.10))
    ax1.legend(bbox_to_anchor=(1.02, .5), loc='center left', borderaxespad=0.)
    plt.savefig(figtit)
    plt.close()




if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2019)

    args = parser.parse_args()
    
    initiate(args.year)

