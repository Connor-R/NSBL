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

    print '\t', year, 'NSBL Team Pennant Odds'    
    plot_all(year, 'Pennant Odds')

    print '\t', year, 'NSBL Team World Series Odds'    
    plot_all(year, 'World Series Odds')


    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nexport_leaderboards.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def plot_all(year, plot_type):

    if plot_type == "World Series Odds":
        qry_add = "win_ws"
    elif plot_type == "Pennant Odds":
        qry_add = "make_ws"

    fig = plt.figure(figsize=(10,10))
    
    ax1 = plt.axes([0.08, 0.08, 0.80, 0.85]) 
    plt.grid()

    figtit = path + str(year) + '_NSBL_inPlayoff_' + plot_type.replace(' ','') + '-Projections' + '.png'

    plt.title(str(year) + ' - ' + plot_type + ' - In Playoff Projections', fontsize = 20)

    teams = db.query("select distinct(team_name) from __in_playoff_probabilities where year =" + str(year) + ";")
    
    for i, t in enumerate(teams):
        team_name = t[0]

        t_qry = """SELECT 
        team_abb, total_playoff_games_played, 
        %s
        FROM __in_playoff_probabilities
        WHERE strength_type = "projected"
        AND win_ws IS NOT NULL
        AND year = %s
        AND team_name = "%s"
        ORDER BY total_playoff_games_played ASC;"""

        t_query = t_qry % (qry_add, year, team_name)

        x_list = []
        y_list = []
        res = db.query(t_query)

        for j, row in enumerate(res):
            list_label, x_val, y_val = row

            x_list.append(j)
            y_list.append(y_val)

            if y_val == 0:
                break

        x = np.array(x_list)
        y = np.array(y_list)

        ax1.scatter(x, y, s=40)

        if int(i/10) == 0:
            linestyle =  '-'
        elif int(i/10) == 1:
            linestyle = '--'
        elif int(i/10) == 2:
            linestyle = '-.'

        ax1.plot(x, y, linewidth=4, linestyle=linestyle, label=list_label.upper())
       
        ax1.set_xlabel('Playoff Days')
        ax1.set_ylabel(plot_type)
        ax1.tick_params('n')

        for label in ax1.get_xticklabels():
            label.set_fontproperties(desired_font)
        for label in ax1.get_yticklabels():
            label.set_fontproperties(desired_font)


    wc_games = 1
    div_games = 5
    cs_games = 12
    ax1.plot([wc_games,wc_games], [0,1], alpha=0.5, color='b', linewidth=2, linestyle='--', label='WC\nRound\nEnd')
    ax1.plot([div_games,div_games], [0,1], alpha=0.5, color='r', linewidth=2, linestyle='--', label='DS\nRound\nEnd')
    ax1.plot([cs_games,cs_games], [0,1], alpha=0.5, color='g', linewidth=2, linestyle='--', label='CS\nRound\nEnd')

    ax1.set_ylim([-0.005,1.005])
    plt.yticks(np.arange(0.00, 1.005, 0.10))

    ax1.legend(bbox_to_anchor=(1.02, .5), loc='center left', borderaxespad=0.)
    plt.savefig(figtit)
    plt.close()




if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2018)

    args = parser.parse_args()
    
    initiate(args.year)

