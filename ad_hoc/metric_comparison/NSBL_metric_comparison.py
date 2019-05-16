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


# Investigating how well zips projects babip onto the sim


db = db('NSBL')


def initiate():

    path = os.getcwd()+'/'

    for hb in ('hitters', 'pitchers'):
        zips_list = []
        observed_list = []

        process(zips_list, observed_list, hb)

        plot(zips_list, observed_list, path, 'zips', 'observed', 'babip', hb)
    

def process(zips_list, observed_list, hb):
    if hb == 'hitters':
        q = """SELECT YEAR, player_name,
        n.babip AS sim_babip, z.babip AS zips_babip
        FROM processed_compWAR_offensive n
        JOIN zips_WAR_hitters_comp z USING (YEAR, player_name)
        WHERE YEAR >= 2011
        AND YEAR < 2019
        AND n.pa > 400;
        """
    else:
        q = """SELECT YEAR, player_name,
        n.babip AS sim_babip, z.babip AS zips_babip
        FROM register_pitching_analytical n
        JOIN zips_WAR_pitchers_comp z USING (YEAR, player_name)
        WHERE YEAR >= 2011
        AND YEAR < 2019
        AND bip > 300;
        """

    qry = q

    res = db.query(qry)

    for row in res:
        year, player_name, sim, zips = row

        zips_list.append(float(zips))
        observed_list.append(float(sim))


def plot(x_list, y_list, path, x_name='x_title', y_name='y_title', val='babip', hb='hitters'):
    size = len(x_list)


    ay_min = min(min(x_list), min(y_list))
    ay_max = max(max(x_list), max(y_list))
    ax_min = min(min(x_list), min(y_list))
    ax_max = max(max(x_list), max(y_list))

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
    figtit = path+"NSBL_comparison_%s_%s_%s_vs_%s.png" % (val, hb, x_name, y_name)

    
    ax.plot(xlims, ylims, linestyle='dashed', alpha=0.9, zorder=0, color='black')
    ax.text(ax_min + ((ax_max-ax_min)/20), ay_max - ((ay_max-ay_min)/10), label, style='normal')
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    fig = ax.get_figure()
    fig.savefig(figtit)
    fig.clf()




if __name__ == "__main__":        

    initiate()

