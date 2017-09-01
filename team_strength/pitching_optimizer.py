from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import math
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

    starter_qry = """SELECT player_name, p.ip as zips_ip, (FIP_WAR/p.ip) AS WAR_per_ip
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

    starter_ip = {"1":220.0, "2":200.0, "3":180.0, "4":150.0, "5":120.0, "6":90.0}
    sp_cnt = 0
    starter_names = []

    starter_val = 0
    total_val = 0
    starter_std = 0
    total_std = 0
    pitching_id = ""
    for row in starters:

        sp_cnt += 1
        sp_ip = starter_ip.get(str(sp_cnt))

        sp_name, zips_ip, WAR_per_ip = row
        sp_WAR = float(WAR_per_ip)*float(sp_ip)
        # fip_std formula from the sigma_research.py script
        fip_std = -0.00042*float(zips_ip) + 0.4823
        # scaling the fip variance to a run value and then to a war value
        run_std = (sp_ip/9.0)*fip_std
        sp_std = run_std/10.0

        s_name = "SP%s_name" % sp_cnt
        s_war = "SP%s_WAR" % sp_cnt
        s_std = "SP%s_std" % sp_cnt

        entry[s_name] = sp_name
        entry[s_war] = sp_WAR
        entry[s_std] = sp_std

        starter_names.append(sp_name)
        total_val += sp_WAR
        starter_val += sp_WAR
        total_std += sp_std ** 2
        starter_std += sp_std ** 2
        pitching_id += sp_name + "_"

    entry["starter_val"] = starter_val

    starter_std = math.sqrt(starter_std)
    entry['starter_std'] = starter_std

    reliever_qry = """SELECT player_name, p.ip as zips_ip, (FIP_WAR/p.ip) AS WAR_per_ip
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

    reliever_ip = {"1":85.0, "2":80.0, "3":75.0, "4":75.0, "5":70.0, "6":65.0, "7":50.0}
    rp_cnt = 0

    bullpen_val = 0
    bullpen_std = 0
    for row in relievers:

        rp_cnt += 1
        rp_ip = reliever_ip.get(str(rp_cnt))

        rp_name, zips_ip, WAR_per_ip = row
        rp_WAR = float(WAR_per_ip)*float(rp_ip)
        # fip_std formula from the sigma_research.py script
        fip_std = -0.00319*float(zips_ip) + 0.84659
        # scaling the fip variance to a run value and then to a war value
        run_std = (rp_ip/9.0)*fip_std
        rp_std = run_std/10.0

        r_name = "RP%s_name" % rp_cnt
        r_war = "RP%s_WAR" % rp_cnt
        r_std = "RP%s_std" % rp_cnt

        entry[r_name] = rp_name
        entry[r_war] = rp_WAR
        entry[r_std] = rp_std

        starter_names.append(rp_name)
        total_val += rp_WAR
        bullpen_val += rp_WAR
        total_std += rp_std ** 2
        bullpen_std += rp_std ** 2
        pitching_id += rp_name + "_"


    entry['bullpen_val'] = bullpen_val

    bullpen_std = math.sqrt(bullpen_std)
    entry['bullpen_std'] = bullpen_std

    pitching_id = pitching_id[:-1].replace(' ','')

    total_std = math.sqrt(bullpen_std**2 + starter_std**2)

    entry['pitching_id'] = pitching_id
    entry['total_val'] = total_val
    entry['total_std'] = total_std

    db.insertRowDict(entry, '__optimal_pitching', insertMany=False, replace=True, rid=0,debug=1)
    db.conn.commit()


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process()
    