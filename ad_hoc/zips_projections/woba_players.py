from py_db import db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import argparse
import csv


# Investigating how park_adjusted zips_wOBA projects observed park_adjusted wOBA in the sim


db = db('NSBL')



def initiate():

    path = '/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/ad_hoc/zips_projections/'

    file_ext = 'woba_players.csv'
    file_name = path+file_ext

    woba_comp = open(file_name, 'wb')
    append_woba_comp = csv.writer(woba_comp)
    header = ['year', 'player_name', 'n_pa', 'n_team', 'n_pf', 'n_PARK_woba', 'z_team', 'z_pf', 'z_PARK_woba', 'woba_PARK_diff', 'n_woba', 'z_woba', 'woba_diff']
    append_woba_comp.writerow(header)

    z_woba_list = []
    n_woba_list = []
    for year in range (2011, 2017):
        process(year, append_woba_comp, z_woba_list, n_woba_list)

    plot(z_woba_list, n_woba_list, path)

def process(year, append_woba_comp, z_woba_list, n_woba_list):

    player_q = """SELECT
search_name,
nsbl.position,
bats,
age,
n_pa, 
n_team,
n_pf,
n_woba,
z_team,
z_pf,
z_woba
FROM (
    SELECT
    player_name,
    CASE WHEN (RIGHT(player_name, 1) IN ('*','#')) THEN LEFT(player_name, LENGTH(player_name)-1)
    ELSE player_name 
    END AS search_name,
    team_abb as n_team,
    pf AS n_pf,
    position, 
    bats, 
    age,
    pa AS n_pa,
    park_wOBA AS n_woba
    FROM processed_compWAR_offensive p
    WHERE year = %s
    AND pa > 500
) nsbl
JOIN (
    SELECT
    player_name,
    position,
    park_woba AS z_woba,
    team_abb AS z_team,
    pf AS z_pf
    FROM zips_processed_WAR_hitters_%s
) zips ON (nsbl.search_name = zips.player_name AND nsbl.position = zips.position)
"""
    player_qry = player_q % (year, year)

    player_list = db.query(player_qry)

    for player in player_list:
        player_name, position, bats, age, n_pa, n_team, n_pf, n_PARK_woba, z_team, z_pf, z_PARK_woba = player

        # print str(year) + '\t' + str(player_name)

        woba_PARK_diff = n_PARK_woba - z_PARK_woba

        n_woba = n_PARK_woba*n_pf
        z_woba = z_PARK_woba*z_pf
        woba_diff = n_woba - z_woba

        row = [year, player_name, n_pa, n_team, n_pf, n_PARK_woba, z_team, z_pf, z_PARK_woba, woba_PARK_diff, n_woba, z_woba, woba_diff]
        append_woba_comp.writerow(row)

        z_woba_list.append(float(z_PARK_woba))
        n_woba_list.append(float(n_PARK_woba))



def plot(x_list, y_list, path):
    size = len(x_list)
    data = pd.DataFrame(
        {'zips_park_adjusted_woba':x_list,
        'nsbl_park_adjusted_woba':y_list
        })

    ay_min = 0.200
    ay_max = 0.450
    ax_min = 0.200
    ax_max = 0.450

    ylims = [ay_min,ay_max]
    xlims = [ax_min,ax_max]

    fit = linregress(x_list,y_list)
    label = '$slope = ' + str(fit.slope) + '$ \n $r^2 = ' + str(fit.rvalue) + '$'

    ax = sns.regplot(x="zips_park_adjusted_woba", y="nsbl_park_adjusted_woba", data=data, ci=None)
    
    ax.plot(xlims, ylims, linestyle='dashed', alpha=0.9, zorder=0, color='black')
    ax.text(ax_min + ((ax_max-ax_min)/20), ay_max - ((ay_max-ay_min)/10), label, style='normal')
    ax.set_title("ZiPS Projected vs DMB Observed wOBA Comparison: Sample Size = " + str(size))
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    figtit = path+"woba_players.png"
    fig = ax.get_figure()
    fig.savefig(figtit)
    fig.clf()



if __name__ == "__main__":        

    initiate()

