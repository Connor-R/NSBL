# RESULTS
# hitters (wOBA) - sigma = -0.00001(zips_pa) + 0.03278
# SP (FIP) - sigma = -0.00042(zips_ip) + 0.4823
# RP (FIP) - sigma = -0.00319(zips_ip) + 0.84659

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


db = db("NSBL")

def initiate():
    path = os.getcwd()

    hit_x_list = []
    hit_y_list = []

    process_hitters(hit_x_list, hit_y_list)

    hit_title = 'Full Season Hitter Sigma research'
    hit_x_title = 'zips_projected PA' 
    hit_y_title = 'wOBA diff StdDev'

    plot(hit_x_list, hit_y_list, path, hit_x_title, hit_y_title, hit_title)

    sp_x_list = []
    sp_y_list = []

    process_pitchers(sp_x_list, sp_y_list, 'sp')

    sp_title = 'Full Season SP Sigma research'
    sp_x_title = 'zips_projected IP' 
    sp_y_title = 'FIP diff StdDev'

    plot(sp_x_list, sp_y_list, path, sp_x_title, sp_y_title, sp_title)

    rp_x_list = []
    rp_y_list = []

    process_pitchers(rp_x_list, rp_y_list, 'rp')

    rp_title = 'Full Season RP Sigma research'
    rp_x_title = 'zips_projected IP' 
    rp_y_title = 'FIP diff StdDev'

    plot(rp_x_list, rp_y_list, path, rp_x_title, rp_y_title, rp_title)


def process_hitters(x_list, y_list):
    qry = """SELECT bin, COUNT(*) AS bin_cnt,
    AVG(zips_pa),
    AVG(sim_wOBA), STDDEV(sim_wOBA),
    AVG(zips_wOBA), STDDEV(sim_wOBA),
    AVG(wOBA_diff), STDDEV(wOBA_diff)
    FROM(
        SELECT YEAR, player_name, 
        n.pa AS sim_pa, z.pa AS zips_pa, 
        IF(z.pa<300,'<300',round((z.pa-25)/50)*50) AS 'bin',
        n.park_wOBA AS sim_wOBA, 
        z.park_wOBA AS zips_wOBA, 
        n.park_wOBA-z.park_wOBA AS wOBA_diff
        FROM processed_compWAR_offensive n
        JOIN zips_WAR_hitters_comp z USING (YEAR, player_name)
        WHERE YEAR >= 2011
        AND n.pa > 400
    ) a
    GROUP BY bin
    HAVING bin_cnt > 25
    ORDER BY AVG(zips_pa) ASC;"""

    res = db.query(qry)

    for row in res:
        foo, foo, zips_pa, foo, foo, foo, foo, foo, wOBA_diff_stddev = row

        x_list.append(float(zips_pa))
        y_list.append(float(wOBA_diff_stddev))

    # sigma = -0.00001(zips_pa) + 0.03278

def process_pitchers(x_list, y_list, role):
    if role == 'sp':
        min_ip = 100
        bin_filt = "IF(z.ip<100,'<100',round((z.ip-10)/20)*20)"
    elif role == 'rp':
        min_ip = 40
        bin_filt = "IF(z.ip<20,'<20',round((z.ip-5)/10)*10)"
    query = """SELECT bin, COUNT(*) AS bin_cnt,
AVG(zips_ip), AVG(sim_ip),
AVG(sim_FIP),
AVG(zips_FIP),
AVG(FIP_diff),
STDDEV(FIP_diff)
FROM(
    SELECT YEAR, player_name, 
    IF(z_bas.gs/z_bas.g > 0.75, 'sp', 'rp') AS proj_role,
    IF(n_bas.gs/n_bas.g > 0.75, 'sp', 'rp') AS sim_role,
    n.ip AS 'sim_ip', z.ip AS 'zips_ip', 
    %s AS 'bin',
    n.park_FIP AS 'sim_FIP', z.park_FIP AS 'zips_FIP',
    (n.park_FIP-z.park_FIP) AS 'FIP_diff'
    FROM processed_WAR_pitchers n
    JOIN zips_WAR_pitchers z USING (YEAR, player_name)
    JOIN zips_pitching z_bas USING (YEAR, player_name)
    JOIN register_pitching_primary n_bas USING (YEAR, player_name)
    WHERE YEAR >= 2011
) a
WHERE proj_role = '%s'
AND sim_role = '%s'
AND sim_ip > %s
GROUP BY bin
HAVING bin_cnt > 25
ORDER BY AVG(zips_IP) ASC;"""

    qry = query % (bin_filt, role, role, min_ip)

    print qry

    res = db.query(qry)

    for row in res:
        foo, foo, zips_ip, foo, foo, foo, foo, FIP_diff_stddev = row

        x_list.append(float(zips_ip))
        y_list.append(float(FIP_diff_stddev))

    # SP - sigma = -0.00042(zips_ip) + 0.4823
    # RP - sigma = -0.00319(zips_ip) + 0.84659

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

    ylims = [ay_min,ay_max]
    xlims = [ax_min,ax_max]

    fit = linregress(x_list,y_list)
    label = '$y = ' + str(round(fit.slope,5))+"x + " + str(round(fit.intercept,5)) + '$ \n$r^2 = ' + str(fit.rvalue) + '$'
    # label = '$r^2 = ' + str(fit.rvalue) + '$'

    data = pd.DataFrame(
        {x_name:x_list,
        y_name:y_list
        })

    g = sns.regplot(x=x_name, y=y_name, data=data, ci=None, fit_reg=True)

    g.set_title(figname)
    figtit = path + '/' + figname + ".png"

    # g.plot(xlims, ylims, linestyle='dashed', alpha=0.9, zorder=0, color='black')
    g.text(ax_min + ((ax_max-ax_min)/25), ay_max - ((ay_max-ay_min)/10), label, style='normal', fontsize=10, horizontalalignment='left', verticalalignment='center')
    g.set_xlim(xlims)
    g.set_ylim(ylims)


    fig = g.get_figure()
    # return fig

    fig.savefig(figtit)
    fig.clf()


if __name__ == "__main__":     
    initiate()

