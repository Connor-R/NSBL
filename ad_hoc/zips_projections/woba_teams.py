from py_db import db
import pandas as pd
import argparse
import csv


# Investigating how park_adjusted zips_wOBA projects observed park_adjusted wOBA in the sim


db = db('NSBL')



def initiate():

    path = '/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/ad_hoc/zips_projections/'

    for team_type in ('n','z'):
        file_ext = 'woba_teams_%s.csv' % team_type
        file_name = path+file_ext

        woba_comp = open(file_name, 'wb')
        
        append_woba_comp = csv.writer(woba_comp)
        header = ['year', 'team', 'pf', 'n_pa', 'n_woba', 'z_woba', 'diff']
        append_woba_comp.writerow(header)

        for year in range (2011, 2018):
            process(year, append_woba_comp, team_type)

def process(year, append_woba_comp, team_type):

        player_q = """SELECT
%s_team,
%s_pf,
AVG(n_pa), 
AVG(n_woba),
AVG(z_woba),
AVG(n_woba-z_woba) AS diff
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
GROUP BY %s_team
ORDER BY diff ASC
"""
        player_qry = player_q % (team_type, team_type, year, year, team_type)

        player_list = db.query(player_qry)

        for player in player_list:
            team, pf, n_pa, n_woba, z_woba, diff = player

            row = [year, team, pf, n_pa, n_woba, z_woba, diff]
            append_woba_comp.writerow(row)

            # plot the data x(z_woba), y(n_woba)

if __name__ == "__main__":        

    initiate()

