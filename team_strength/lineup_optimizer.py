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

    # Each time we run this, we clear the pre-existing table
    db.query("TRUNCATE TABLE `__optimal_lineups`")

    i = 0 

    team_q = """SELECT DISTINCT team_abb
    FROM teams 
    -- FROM excel_rosters
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

    tq_add = "AND team_abb = '%s'" % team_abb
    tq_add2 = "AND t.team_abb = '%s'" % team_abb
    # tq_add2 = "AND cre.team_abb = '%s'" % team_abb


    for lu_type in ('all', 'r', 'l'):
        for dh_type in ('with', 'without'):
            if lu_type == 'all':
                war_type = 'WAR'
            else:
                war_type = 'vs%s_WAR' % (lu_type)

            print '\t' + lu_type + ', ' + dh_type + ' DH'
            
            matrix = []

            base_q = """
    FROM (
    SELECT DISTINCT CONCAT(nm2.right_fname, ' ', nm2.right_lname) AS real_name
    , z.player_name AS player_name
    , t.team_abb
    -- , cre.team_abb
    , (zo.ab+zo.bb+zo.hbp+zo.sh+zo.sf) as 'zips_pa'
    -- SELECT DISTINCT player_name, COALESCE(t.team_abb, cre.team_abb) AS team_abb, (zo.ab+zo.bb+zo.hbp+zo.sh+zo.sf) as 'zips_pa'
    FROM zips_WAR_hitters z
    JOIN zips_offense zo ON (z.player_name = zo.player_name 
        AND z.year = zo.year 
        AND z.team_abb = zo.team_abb 
        AND z.age = zo.age
    )
    JOIN name_mapper nm ON (1
        AND z.player_name = nm.wrong_name
        AND (nm.start_year IS NULL OR nm.start_year <= z.year)
        AND (nm.end_year IS NULL OR nm.end_year >= z.year)
        AND (nm.position = '' OR nm.position = z.position)
        AND (nm.rl_team = '' OR nm.rl_team = z.team_abb)
        # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
    )
    JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
        AND nm.right_lname = nm2.right_lname
        AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
        AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
        AND (nm.position = '' OR nm.position = nm2.position)
        AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
    )
    JOIN current_rosters c ON (nm2.wrong_name = c.player_name
        AND c.position NOT IN ('SP', 'MR', 'CL')
    )
    JOIN teams t ON (c.team_id = t.team_id 
        AND z.year = t.year
    )
    -- LEFT JOIN processed_WAR_hitters w ON (z.year = w.year AND z.age = w.age AND nm2.wrong_name = w.player_name)
    -- LEFT JOIN(
    --     SELECT e.*
    --     FROM excel_rosters e
    --     JOIN (
    --         SELECT year
    --         , MAX(date) AS date
    --         FROM excel_rosters
    --         WHERE 1
    --             AND year = %s
    --     ) cur USING (year, date)
    -- ) cre ON (IFNULL(nm2.wrong_name, z.player_name) = cre.player_name)
    WHERE 1
        AND z.year = %s
    --    AND (cre.salary_counted IS NULL OR cre.salary_counted != 'N' OR w.player_name IS NOT NULL)
    HAVING 1
        %s
        AND player_name NOT IN ('Player Name', 'Harrison Bader', 'Luis Arraez', 'Willy Adames')
    ) base"""

            base_q = base_q % (year, year, tq_add)

            # raw_input(base_q)
            positions = ('dh', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf')
            a = 0
            position_map = {}
            q_sel = """SELECT real_name AS player_name
            , team_abb
            , zips_pa
            , dh_WAR
            , c_WAR
            , 1b_WAR
            , 2b_WAR
            , 3b_WAR
            , ss_WAR
            , lf_WAR
            , cf_WAR
            , rf_WAR
            """
            q = q_sel+base_q
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

            cnt_q = """SELECT COUNT(*)
            FROM(
                %s
            ) a
            """

            cnt_qry = cnt_q % (q)
            # raw_input(cnt_qry)
            cnt = db.query(cnt_qry)[0][0]

            # if team_abb.upper() == 'TAM':
                # raw_input(q)
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
                    woba_std = -0.0000028765*float(zips_pa) + 0.0251773378
                    
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
    parser.add_argument('--year',default=2020)
    args = parser.parse_args()
    
    process(args.year)
    

