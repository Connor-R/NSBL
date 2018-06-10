# RESULTS
# 
# hitters (wOBA) - std = -0.0000083283(zips_pa) + 0.0277557512
# SP (FIP) - std = -0.000169247(zips_ip) + 0.3625156228
# RP (FIP) - std = -0.0005925607(zips_ip) + 0.5332422101
# team (std in wins) - expected std = -0.0052542947(expected_wins) + 3.4279721907

from py_db import db
import numpy as np
import pandas as pd
import argparse
import os
from datetime import date,timedelta
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn as sns
from time import time


# Recall, std = sqrt(E[(X-µ)^2]), or abs(E(X-µ))


db = db("NSBL")


def initiate():
    path = os.getcwd()

    hit_x_list = []
    hit_y_list = []
    process_hitters(hit_x_list, hit_y_list)
    hit_title = 'Full Season Hitter std research'
    hit_x_title = 'zips_projected PA' 
    hit_y_title = 'wOBA diff'
    plot(hit_x_list, hit_y_list, path, hit_x_title, hit_y_title, hit_title)

    sp_x_list = []
    sp_y_list = []
    process_pitchers(sp_x_list, sp_y_list, 'sp')
    sp_title = 'Full Season SP std research'
    sp_x_title = 'zips_projected IP' 
    sp_y_title = 'FIP diff'
    plot(sp_x_list, sp_y_list, path, sp_x_title, sp_y_title, sp_title)

    rp_x_list = []
    rp_y_list = []
    process_pitchers(rp_x_list, rp_y_list, 'rp')
    rp_title = 'Full Season RP std research'
    rp_x_title = 'zips_projected IP' 
    rp_y_title = 'FIP diff'
    plot(rp_x_list, rp_y_list, path, rp_x_title, rp_y_title, rp_title)


    pythag_x_list = []
    pythag_y_list = []
    process_pythag(pythag_x_list, pythag_y_list)
    pythag_title = 'Full Season Pythag Standings std research'
    pythag_x_title = 'pythagorean wins'
    pythag_y_title = 'Wins diff'
    plot(pythag_x_list, pythag_y_list, path, pythag_x_title, pythag_y_title, pythag_title)


def process_hitters(x_list, y_list):
    qry = """SELECT YEAR, player_name, 
    n.pa AS sim_pa, z.pa AS zips_pa,
    ABS(n.park_wOBA-z.park_wOBA) AS wOBA_std
    FROM processed_compWAR_offensive n
    JOIN zips_WAR_hitters_comp z USING (YEAR, player_name)
    WHERE YEAR >= 2011
    AND YEAR < 2018
    AND n.pa > 400;"""

    res = db.query(qry)

    for row in res:
        foo, foo, foo, zips_pa, wOBA_diff_stddev = row

        x_list.append(float(zips_pa))
        y_list.append(float(wOBA_diff_stddev))


def process_pitchers(x_list, y_list, role):
    if role == 'sp':
        min_ip = 100
    elif role == 'rp':
        min_ip = 40

    query = """SELECT 
    YEAR, player_name
    proj_role, sim_role,
    sim_ip, zips_ip,
    sim_FIP, zips_FIP,
    ABS(FIP_diff) AS FIP_std
    FROM(
        SELECT YEAR, player_name, 
        IF(z_bas.gs/z_bas.g > 0.75, 'sp', 'rp') AS proj_role,
        IF(n_bas.gs/n_bas.g > 0.75, 'sp', 'rp') AS sim_role,
        n.ip AS 'sim_ip', z.ip AS 'zips_ip', 
        n.park_FIP AS 'sim_FIP', z.park_FIP AS 'zips_FIP',
        (n.park_FIP-z.park_FIP) AS 'FIP_diff'
        FROM processed_WAR_pitchers n
        JOIN zips_WAR_pitchers z USING (YEAR, player_name)
        JOIN zips_pitching z_bas USING (YEAR, player_name)
        JOIN register_pitching_primary n_bas USING (YEAR, player_name)
        WHERE YEAR >= 2011
        AND YEAR < 2018
    ) a
    WHERE proj_role = '%s'
    AND sim_role = '%s'
    AND sim_ip > %s;"""

    qry = query % (role, role, min_ip)

    # print qry

    res = db.query(qry)

    for row in res:
        foo, foo, foo, foo, zips_ip, foo, foo, FIP_diff_stddev = row

        x_list.append(float(zips_ip))
        y_list.append(float(FIP_diff_stddev))


def process_pythag(x_list, y_list):
    qry = """SELECT YEAR, team_name, w, py_wins, ABS(w-py_wins) AS pythag_diff
    FROM processed_team_standings_advanced
    JOIN (SELECT YEAR, team_name, MAX(games_played) AS games_played FROM processed_team_standings_advanced GROUP BY YEAR, team_name) a USING (YEAR, team_name, games_played)
    WHERE games_played >= 150;"""

    res = db.query(qry)

    for row in res:
        foo, foo, foo, py_wins, pythag_diff = row

        x_list.append(float(py_wins))
        y_list.append(float(pythag_diff))


def plot(x_list, y_list, path, x_name='x_title', y_name='y_title', figname = 'fig_name'):
    size = len(x_list)

    if min(min(y_list), min(x_list)) < 0:
        y_min = min(y_list) * 1.10
        x_min = min(x_list) * 1.10
    else:
        y_min = min(y_list) * .9 
        x_min = min(x_list) * .9
    y_max = max(y_list) * 1.10
    x_max = max(x_list) * 1.10

    axes_min = min(y_min, x_min)
    axes_max = max(y_max, x_max)

    ay_min = y_min
    ax_min = x_min
    ay_max = y_max
    ax_max = x_max

    ylims = [-.05,ay_max]
    xlims = [ax_min,ax_max]

    fit = linregress(x_list,y_list)
    label = '$y = ' + str(round(fit.slope,10))+"x + " + str(round(fit.intercept,10)) + '$'
    print '\n',figname
    print '\t', label, '\n'
    # label = '$r^2 = ' + str(fit.rvalue) + '$'

    data = pd.DataFrame(
        {x_name:x_list,
        y_name:y_list
        })

    g = sns.regplot(x=x_name, y=y_name, data=data, ci=None, fit_reg=True)

    g.set_title(figname)
    figtit = path + '/' + figname + ".png"

    # g.plot(xlims, ylims, linestyle='dashed', alpha=0.9, zorder=0, color='black')
    g.text(ax_min*1.1, ay_max*0.99, label, style='normal', fontsize=10, horizontalalignment='left', verticalalignment='top')
    g.set_xlim(xlims)
    g.set_ylim(ylims)


    fig = g.get_figure()
    # return fig

    fig.savefig(figtit)
    fig.clf()


if __name__ == "__main__":     
    initiate()

