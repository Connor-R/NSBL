from py_db import db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import argparse
import csv


# Investigating how well yearly observed teamWAR correlates to yearly observed wins within the sim


db = db('NSBL')


mascot_names = {
    "ANA": "Angels",
    "ARI": "Diamondbacks",
    "ATL": "Braves",
    "AZ": "Diamondbacks",
    "AZD": "Diamondbacks",
    "BAL": "Orioles",
    "BOS": "Red Sox",
    "CHA": "White Sox",
    "CHC": "Cubs",
    "CHN": "Cubs",
    "CIN": "Reds",
    "CLE": "Indians",
    "CLV": "Indians",
    "COL": "Rockies",
    "CWS": "White Sox",
    "DET": "Tigers",
    "FLA": "Marlins",
    "FLO": "Marlins",
    "HOU": "Astros",
    "KC": "Royals",
    "KCR": "Royals",
    "LA": "Dodgers",
    "LAA": "Angels",
    "LAD": "Dodgers",
    "LAN": "Dodgers",
    "MIA": "Marlins",
    "MIL": "Brewers",
    "MIN": "Twins",
    "NYA": "Yankees",
    "NYM": "Mets",
    "NYN": "Mets",
    "NYY": "Yankees",
    "OAK": "Athletics",
    "PHI": "Phillies",
    "PIT": "Pirates",
    "SD": "Padres",
    "SDP": "Padres",
    "SEA": "Mariners",
    "SF": "Giants",
    "SFG": "Giants",
    "STL": "Cardinals",
    "TAM": "Rays",
    "TB": "Rays",
    "TBR": "Rays",
    "TEX": "Rangers",
    "TOR": "Blue Jays",
    "WAS": "Nationals"
}


def initiate():

    path = '/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/ad_hoc/'

    file_ext = 'NSBL_standings_comparison.csv'
    file_name = path+file_ext
    _file = open(file_name, 'wb')
    append_file = csv.writer(_file)
    file_header = ['year', 'team_name', 'repWAR', 'fWAR', 'rWAR', 'f_wins', 'r_wins', ' pythag_wins', 'wins']
    append_file.writerow(file_header)

    fip_Wins = []
    era_Wins = []
    pythag_Wins = []
    observed_Wins = []
    for year in range(2006,2017):
        process(year, append_file, fip_Wins, era_Wins, pythag_Wins, observed_Wins)

    plot(pythag_Wins, observed_Wins, path, 'pythag_wins', 'observed_wins')
    plot(fip_Wins, observed_Wins, path, 'fip_wins', 'observed_wins')
    plot(fip_Wins, pythag_Wins, path, 'fip_wins', 'pythag_wins')
    plot(era_Wins, observed_Wins, path, 'era_wins', 'observed_wins')
    plot(era_Wins, pythag_Wins, path, 'era_wins', 'pythag_wins')


def process(year, append_file, f_wins_list, r_wins_list, pythag_wins_list, wins_list):
    teamWAR_q = """SELECT
year,
team_abb,
dWAR,
oWAR,
(replacement/10) as repWAR,
FIP_WAR,
ERA_WAR
FROM processed_WAR_team
WHERE year = %s
"""
    team_WAR_qry = teamWAR_q % year

    team_WAR_list = db.query(team_WAR_qry)

    for team in team_WAR_list:
        year, team_abb, dWAR, oWAR, repWAR, FIP_WAR, ERA_WAR = team

        mascot_name = mascot_names.get(team_abb.upper())

        #a full season is ~17 replacement wins?
        repWAR = float(repWAR)

        pos_WAR = float(dWAR) + float(oWAR) + repWAR
        fWAR = pos_WAR + float(FIP_WAR)
        rWAR = pos_WAR + float(ERA_WAR)

        # print year, team_abb, mascot_name

        if team_abb == '':
            continue
        else:
            record_q = """SELECT
year,
team_name, 
w,
l,
rf,
ra
FROM team_standings
WHERE team_name LIKE '%%%s%%'
AND year = %s
"""
            record_qry = record_q % (mascot_name, year)

            record = db.query(record_qry)[0]

            year, team_name, w, l, rf, ra = record

            w_pct = 0

            # http://www.had2know.com/sports/pythagorean-expectation-win-percentage-baseball.html
            pythag_x = ((float(rf)+float(ra))/(float(w)+float(l)))**(float(0.285))
            pythag_win_pct = (float(rf)**pythag_x)/((float(rf)**pythag_x) + (float(ra)**pythag_x))
            pythag_wins = (w+l)*pythag_win_pct

            games = w+l
            rep_team_win_pct = 0.333
            rep_team_wins = rep_team_win_pct*games

            f_wins = (pos_WAR/repWAR)*17.0 + float(FIP_WAR) + rep_team_wins
            r_wins = (pos_WAR/repWAR)*17.0 + float(ERA_WAR) + rep_team_wins

            row = year, team_name, repWAR, fWAR, rWAR, f_wins, r_wins,  pythag_wins, w

            #write row
            append_file.writerow(row)

            f_wins_list.append(float(f_wins))
            r_wins_list.append(float(r_wins))
            pythag_wins_list.append(float(pythag_wins))
            wins_list.append(float(w))

            # print year, team_name, repWAR, fWAR, rWAR
            # print f_wins, r_wins, pythag_wins, w
            # print '\n'


def plot(x_list, y_list, path, x_name='x_title', y_name='y_title'):
    size = len(x_list)


    ay_min = 30.0
    ay_max = 140.0
    ax_min = 30.0
    ax_max = 140.0

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

