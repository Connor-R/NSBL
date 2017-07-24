from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import numpy as np

# script that estiamtes value for each teams best projected 13 man pitching staff


db = db('NSBL')


def process():
    start_time = time()

    #Each time we run this, we clear the pre-existing table
    db.query("TRUNCATE TABLE `__optimal_pitching`")

    i = 0 

    team_q = """SELECT DISTINCT team_abb FROM teams 
    WHERE year = 2017
    ORDER BY team_abb ASC
    """
    team_qry = team_q
    teams = db.query(team_qry)
    for team in teams:
        team_abb = team[0]

        i += 1
        print i, team_abb

        get_pitchers(team_abb)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "pitching_optimizer.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def get_pitchers(team_abb):
    entry = {}

    entry['team_abb'] = team_abb

    starter_qry = """SELECT player_name, (FIP_WAR/p.ip) AS WAR_per_ip
    FROM zips_pitching p
    LEFT JOIN zips_WAR_pitchers z USING (YEAR, player_name, team_abb)
    LEFT JOIN current_rosters c USING (YEAR, player_name)
    LEFT JOIN teams t USING (YEAR, team_id)
    WHERE z.year = 2017
    AND t.team_abb = '%s'
    AND (gs/g) > 0.5
    ORDER BY WAR_per_ip DESC
    LIMIT 6;"""

    starter_query = starter_qry % (team_abb)

    starters = db.query(starter_query)

    starter_ip = {"1":220, "2":200, "3":180, "4":150, "5":120, "6":90}
    sp_cnt = 0
    starter_names = []

    starter_val = 0
    total_val = 0
    pitching_id = ""
    for row in starters:

        sp_cnt += 1
        sp_ip = starter_ip.get(str(sp_cnt))

        sp_name, WAR_per_ip = row
        sp_WAR = float(WAR_per_ip)*float(sp_ip)

        s_name = "SP%s_name" % sp_cnt
        s_war = "SP%s_WAR" % sp_cnt

        entry[s_name] = sp_name
        entry[s_war] = sp_WAR

        starter_names.append(sp_name)
        total_val += sp_WAR
        starter_val += sp_WAR
        pitching_id += sp_name + "_"

    entry["starter_val"] = starter_val

    reliever_qry = """SELECT player_name, (FIP_WAR/p.ip) AS WAR_per_ip
    FROM zips_pitching p
    LEFT JOIN zips_WAR_pitchers z USING (YEAR, player_name, team_abb)
    LEFT JOIN current_rosters c USING (YEAR, player_name)
    LEFT JOIN teams t USING (YEAR, team_id)
    WHERE z.year = 2017
    AND t.team_abb = '%s'
    AND player_name NOT IN %s
    ORDER BY WAR_per_ip DESC
    LIMIT 7;"""

    reliever_query = reliever_qry % (team_abb, tuple(starter_names))

    relievers = db.query(reliever_query)

    reliever_ip = {"1":85, "2":80, "3":75, "4":75, "5":70, "6":65, "7":50}
    rp_cnt = 0

    reliever_val = 0
    for row in relievers:

        rp_cnt += 1
        rp_ip = reliever_ip.get(str(rp_cnt))

        rp_name, WAR_per_ip = row
        rp_WAR = float(WAR_per_ip)*float(rp_ip)

        r_name = "RP%s_name" % rp_cnt
        r_war = "RP%s_WAR" % rp_cnt

        entry[r_name] = rp_name
        entry[r_war] = rp_WAR

        starter_names.append(rp_name)
        total_val += rp_WAR
        reliever_val += rp_WAR
        pitching_id += rp_name + "_"


    entry["reliever_val"] = reliever_val

    pitching_id = pitching_id[:-1].replace(' ','')

    entry['pitching_id'] = pitching_id
    entry['total_val'] = total_val

    db.insertRowDict(entry, '__optimal_pitching', insertMany=False, replace=True, rid=0,debug=1)
    db.conn.commit()


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process()
    