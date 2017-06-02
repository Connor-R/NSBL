from py_db import db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import argparse
import csv


# Investigating how park_adjusted zips_ERA and zips_FIP projects observed park_adjusted ERA and FIP in the sim


db = db('NSBL')



def initiate():

    path = '/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/ad_hoc/zips_projections/'

    fip_ext = 'pitching_fip_players.csv'
    fip_name = path+fip_ext
    fip_comp = open(fip_name, 'wb')
    append_fip_comp = csv.writer(fip_comp)
    fip_header = ['year','player_name','n_ip','n_team','n_pf','n_FIP','z_team','z_pf','z_FIP','diff']
    append_fip_comp.writerow(fip_header)


    era_ext = 'pitching_era_players.csv'
    era_name = path+era_ext
    era_comp = open(era_name, 'wb')
    append_era_comp = csv.writer(era_comp)
    era_header = ['year','player_name','n_ip','n_team','n_pf','n_ERA','z_team','z_pf','z_ERA','diff']
    append_era_comp.writerow(era_header)


    _type_list = []
    zips_list = []
    nsbl_list = []

    zips_era_list = []
    nsbl_era_list = []
    zips_fip_list = []
    nsbl_fip_list = []
    for _type in ('era','fip'):
        if _type == 'era':    
            process(append_era_comp, zips_era_list, nsbl_era_list, _type, zips_list, nsbl_list, _type_list)
        elif _type == 'fip':
            process(append_fip_comp, zips_fip_list, nsbl_fip_list, _type, zips_list, nsbl_list, _type_list)



    for _type in ('era', 'fip'):
        if _type == 'era':    
            plot(zips_era_list, nsbl_era_list, _type, path)
        elif _type == 'fip':
            plot(zips_fip_list, nsbl_fip_list, _type, path)

    plot2(zips_list, nsbl_list, _type_list, path)


def process(append_comp, zips_metric_list, nsbl_metric_list, _type, zips_list, nsbl_list, _type_list):

    player_q = """SELECT
search_name,
nsbl.year,
zips.year,
n_ip,
n_team,
n_pf,
n_%s,
z_team,
z_pf,
z_%s,
(n_%s - z_%s) as diff
FROM (
    SELECT
    player_name, year,
    CASE 
        WHEN (RIGHT(player_name, 1) IN ('*','#')) THEN LEFT(player_name, LENGTH(player_name)-1)
        ELSE player_name 
        END AS search_name,
    team_abb as n_team,
    pf AS n_pf,
    ip AS n_ip,
    park_%s AS n_%s
    FROM processed_WAR_pitchers p
    WHERE ip > 60
) nsbl
JOIN (
    SELECT
    player_name, year,
    park_%s AS z_%s,
    team_abb AS z_team,
    pf AS z_pf
    FROM zips_WAR_pitchers
) zips ON (nsbl.search_name = zips.player_name AND nsbl.year = zips.year)
"""
    player_qry = player_q % (_type, _type, _type, _type, _type, _type, _type, _type)
    # raw_input(player_qry)

    player_list = db.query(player_qry)

    for player in player_list:
        player_name, year1, year2, n_ip, n_team, n_pf, n_metric, z_team, z_pf, z_metric, diff = player

        row = [year1, player_name, n_ip, n_team, n_pf, n_metric, z_team, z_pf, z_metric, diff]

        append_comp.writerow(row)
        zips_metric_list.append(float(z_metric))
        nsbl_metric_list.append(float(n_metric))

        zips_list.append(float(z_metric))
        nsbl_list.append(float(n_metric))
        _type_list.append(_type)

def plot(x_list, y_list, _type, path):
    size = len(x_list)


    ay_min = 1.0
    ay_max = 8.0
    ax_min = 1.0
    ax_max = 8.0

    ylims = [ay_min,ay_max]
    xlims = [ax_min,ax_max]

    fit = linregress(x_list,y_list)
    label = '$slope = ' + str(fit.slope) + '$ \n $r^2 = ' + str(fit.rvalue) + '$'

    if _type == 'era':
        data = pd.DataFrame(
            {'zips_park_adjusted_era':x_list,
            'nsbl_park_adjusted_era':y_list
            })
        ax = sns.regplot(x="zips_park_adjusted_era", y="nsbl_park_adjusted_era", data=data, ci=None)
        ax.set_title("ZiPS Projected vs DMB Observed ERA Comparison: Sample Size = " + str(size)) 
        figtit = path+"pitching_chart_era.png"
    elif _type == 'fip':
        data = pd.DataFrame(
            {'zips_park_adjusted_fip':x_list,
            'nsbl_park_adjusted_fip':y_list
            })
        ax = sns.regplot(x="zips_park_adjusted_fip", y="nsbl_park_adjusted_fip", data=data, ci=None)
        ax.set_title("ZiPS Projected vs DMB Observed FIP Comparison: Sample Size = " + str(size)) 
        figtit = path+"pitching_chart_fip.png"

    
    ax.plot(xlims, ylims, linestyle='dashed', alpha=0.9, zorder=0, color='black')
    ax.text(ax_min + ((ax_max-ax_min)/20), ay_max - ((ay_max-ay_min)/10), label, style='normal')
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    fig = ax.get_figure()
    fig.savefig(figtit)
    fig.clf()


def plot2(x_list, y_list, _type_list, path):
    size = len(x_list)
    data = pd.DataFrame(
        {'zips_park_adjusted_metric':x_list,
        'nsbl_park_adjusted_metric':y_list,
        '_type':_type_list
        })

    ay_min = 1.0
    ay_max = 8.0
    ax_min = 1.0
    ax_max = 8.0

    ylims = [ay_min,ay_max]
    xlims = [ax_min,ax_max]

    fit = linregress(x_list,y_list)
    label = '$For all data: \n $slope = ' + str(fit.slope) + '$ \n $r^2 = ' + str(fit.rvalue) + '$'

    ax = sns.lmplot(x="zips_park_adjusted_metric", y="nsbl_park_adjusted_metric", hue='_type', data=data, ci=None)
    
    figtit = path+"pitching_chart_both.png"
    plt.axis((ax_min,ax_max,ay_min,ay_max))
    plt.savefig(figtit)
    plt.clf()


if __name__ == "__main__":        

    initiate()

