from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
import itertools
from time import time
from scipy import optimize
import math
import numpy as np


# script that determines the best possible lineup for all teams.
# it uses the hungarian algorithm (and some hacky tricks) to solve this assignment problem. 


db = db('NSBL')


def process(year):
    start_time = time()

    #Each time we run this, we clear the pre-existing table
    db.query("TRUNCATE TABLE `__optimal_lineups`")

    i = 0 

    team_q = """SELECT DISTINCT team_abb FROM teams 
    WHERE year = %s
    ORDER BY team_abb ASC
    """
    team_qry = team_q % (year)
    teams = db.query(team_qry)
    for team in teams:
        team_abb = team[0]

        i += 1
        print i, team_abb

        get_player_matrix(team_abb, year)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "lineup_optimizer.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def get_player_matrix(team_abb, year):

    tq_add = "AND t.team_abb = '%s'" % team_abb

    for lu_type in ('all', 'r', 'l'):
        for dh_type in ('with', 'without'):
            if lu_type == 'all':
                war_type = 'WAR'
            else:
                war_type = 'vs%s_WAR' % (lu_type)

            print '\t' + lu_type + ', ' + dh_type + ' DH'
            
            matrix = []

            q = """SELECT *
    FROM (
    SELECT DISTINCT player_name, t.team_abb, (zo.ab+zo.bb+zo.hbp+zo.sh+zo.sf) as 'zips_pa'
    FROM zips_WAR_hitters z
    JOIN zips_offense zo USING (player_name, year, team_abb, age)
    LEFT JOIN processed_WAR_hitters w USING (YEAR, player_name, age)
    LEFT JOIN current_rosters c USING (player_name, year)
    LEFT JOIN teams t USING (team_id, year)
    LEFT JOIN(
        SELECT *
        FROM excel_rosters
        JOIN (
            SELECT year
            , MAX(gp) AS gp
            FROM excel_rosters
            WHERE 1
                AND year = %s
        ) cur USING (year, gp)
    ) cre USING (player_name)
    WHERE z.year = %s
    AND player_name NOT IN ('Player Name', 'Ronald Acuna', 'Gleyber Torres', 'Brendan Rodgers', 'Max Kepler')
    # AND (cre.salary_counted IS NULL OR cre.salary_counted != 'N' OR w.player_name IS NOT NULL)
    %s
    ) base"""

            q = q % (year, year, tq_add)

            positions = ('dh', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf')
            a = 0
            position_map = {}
            for pos in positions:
                position_map[a]=pos
                a += 1

                q_add = """\nLEFT JOIN (
    SELECT player_name, %s AS '%s_WAR'
    FROM zips_WAR_hitters z
    WHERE z.year = %s
    AND z.position = '%s'
    ) _%s USING (player_name)"""

                if pos == 'dh' and dh_type == 'without':
                    qry_add = q_add % ('NULL', pos, year, pos, pos)
                else:
                    qry_add = q_add % (war_type, pos, year, pos, pos)

                q += qry_add

            cnt_q = """SELECT COUNT(DISTINCT player_name)
    FROM zips_WAR_hitters z
    LEFT JOIN current_rosters c USING (player_name, YEAR)
    LEFT JOIN teams t USING (team_id, YEAR)
    WHERE z.year = %s
    %s"""

            cnt_qry = cnt_q % (year, tq_add)
            # raw_input(cnt_qry)
            cnt = db.query(cnt_qry)[0][0]

            # if team_abb == 'Tam':
            #     raw_input(q)
            # raw_input(q)
            res = db.query(q)
            j = 0
            player_map = {}
            for row in res:
                player_map[j] = [row[0],row[2]]
                j += 1
                matrix_row = []
                for i in range(0, cnt+3):
                    if i > 11:
                        matrix_row.append(500)
                    elif i >= 3:
                        if row[i] is None:
                            matrix_row.append(500)
                        else:
                            matrix_row.append(100-float(row[i]))

                matrix.append(matrix_row)

            # print matrix
            # raw_input(matrix)
            lu = optimize.linear_sum_assignment(matrix)

            # raw_input(position_map)
            # raw_input(player_map)

            optimized_lu = zip(lu[1],lu[0])
            # raw_input(optimized_lu)
            entry = {}
            entry['team_abb'] = team_abb
            entry['vs_hand'] = lu_type

            total_val = 0
            total_variance = 0
            # https://stats.stackexchange.com/questions/17800/what-is-the-distribution-of-the-sum-of-independent-normal-variables
            for i,v in optimized_lu:
                if i < 9 and (i > 0 or (i >= 0 and dh_type == 'with')):
                    opt_pos = position_map.get(i)
                    p_name = player_map.get(v)[0]
                    # print v,i
                    # raw_input(p_name)
                    war_val = 100.0-matrix[v][i]
                    zips_pa = player_map.get(v)[1]
                    # woba_std formula from the NSBL_std_research.py script
                    woba_std = -0.0000083283*float(zips_pa) + 0.0277557512
                    
                    # add defensive variance??? ##### TODO

                    war_variance = (650.0*woba_std/1.25)/10.0
                    total_val += war_val
                    total_variance += war_variance**2

                    # print opt_pos, p_name, war_val

                    e_name = opt_pos + '_' + 'name'
                    e_war = opt_pos + '_' + 'WAR'
                    e_variance = opt_pos + '_' + 'var'
                    entry[e_name] = p_name
                    entry[e_war] = war_val
                    entry[e_variance] = war_variance
                    # raw_input(entry)

            lineup_id = entry['c_name'] + '_' + entry['1b_name'] + '_' + entry['2b_name'] + '_' + entry['3b_name'] + '_' + entry['ss_name'] + '_' + entry['lf_name'] + '_' + entry['cf_name'] + '_' + entry['rf_name']
            try:
                lineup_id += '_' + entry['dh_name']
            except KeyError:
                lineup_id += '_' + 'NONE'

            lineup_id = lineup_id.replace(' ','')

            entry['lineup_id'] = lineup_id
            entry['lineup_val'] = total_val
            entry['lineup_var'] = total_variance
            # raw_input(entry)

            db.insertRowDict(entry, '__optimal_lineups', insertMany=False, replace=True, rid=0,debug=1)
            db.conn.commit()


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2019)
    args = parser.parse_args()
    
    process(args.year)
    

