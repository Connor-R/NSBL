from py_db import db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import argparse
import csv
import NSBL_helpers as helper
import os


# Investigating how well yearly observed teamWAR correlates to yearly observed wins within the sim


db = db('NSBL')


def initiate():

    path = os.getcwd()+'/'

    fip_Wins = []
    era_Wins = []
    pythag_Wins = []
    observed_Wins = []
    
    process(fip_Wins, era_Wins, pythag_Wins, observed_Wins)

    plot(pythag_Wins, observed_Wins, path, 'pythag_wins', 'observed_wins')
    plot(fip_Wins, observed_Wins, path, 'fip_wins', 'observed_wins')
    plot(fip_Wins, pythag_Wins, path, 'fip_wins', 'pythag_wins')
    plot(era_Wins, observed_Wins, path, 'era_wins', 'observed_wins')
    plot(era_Wins, pythag_Wins, path, 'era_wins', 'pythag_wins')


def process(f_wins_list, r_wins_list, pythag_wins_list, wins_list):
    teamWAR_q = """SELECT
year,
team_name,
games_played,
f_wins,
r_wins,
py_wins,
w
FROM processed_team_standings_advanced
JOIN (SELECT YEAR, team_name, MAX(games_played) AS 'games_played'  FROM processed_team_standings_advanced GROUP BY YEAR, team_name) a USING (YEAR, team_name, games_played)
"""
    team_WAR_qry = teamWAR_q

    team_WAR_list = db.query(team_WAR_qry)

    for team in team_WAR_list:
        year, team_name, games_played, f_wins, r_wins, pythag_wins, w = team


        f_wins_list.append(float(f_wins))
        r_wins_list.append(float(r_wins))
        pythag_wins_list.append(float(pythag_wins))
        wins_list.append(float(w))

        # print year, team_name, repWAR, fWAR, rWAR
        # print f_wins, r_wins, pythag_wins, w
        # print '\n'


def plot(x_list, y_list, path, x_name='x_title', y_name='y_title'):
    size = len(x_list)


    ay_min = 0.0
    ay_max = 162.0
    ax_min = 0.0
    ax_max = 162.0

    ylims = [ay_min,ay_max]
    xlims = [ax_min,ax_max]

    fit = linregress(x_list,y_list)
    label = '$slope = ' + str(fit.slope) + '$ \n $r^2 = ' + str(fit.rvalue) + '$'

    data = pd.DataFrame(
        {x_name:x_list,
        y_name:y_list
        })
    ax = sns.regplot(x=x_name, y=y_name, data=data, ci=None)
    title_str = x_name + ' vs ' + y_name + ': Sample Size = '
    ax.set_title(title_str + str(size)) 
    figtit = path+"NSBL_standings_%s_vs_%s.png" % (x_name, y_name)

    
    ax.plot(xlims, ylims, linestyle='dashed', alpha=0.9, zorder=0, color='black')
    ax.text(ax_min + ((ax_max-ax_min)/20), ay_max - ((ay_max-ay_min)/10), label, style='normal')
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    fig = ax.get_figure()
    fig.savefig(figtit)
    fig.clf()




if __name__ == "__main__":        

    initiate()

