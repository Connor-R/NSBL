from py_db import db
import argparse
from decimal import Decimal

# Goes through the list of projected pitchers and projects their WAR


db = db('NSBL')
park_factors = {
    "ANA":98.33,
    "LAA":98.33,
    "HOU":98.33,
    "OAK":100,
    "TOR":99,
    "ATL":99.67,
    "MIL":101,
    "STL":99.33,
    "CHC":100.67,
    "CHN":100.67,
    "ARI":101.33,
    "AZ":101.33,
    "AZD":101.33,
    "LA":98.67,
    "LAD":98.67,
    "LAN":98.67,
    "SF":97.67,
    "SFG":97.67,
    "CLE":99,
    "CLV":99,
    "SEA":99,
    "FLA":100.33,
    "FLO":100.33,
    "MIA":100.33,
    "NYM":98.33,
    "NYN":98.33,
    "WAN":100,
    "WAS":100,
    "BAL":100.67,
    "BALT":100.67,
    "SAN":98,
    "SD":98,
    "SDP":98,
    "PHI":100,
    "PIT":99,
    "TEX":102,
    "TAM":98.33,
    "TB":98.33,
    "TBA":98.33,
    "TBR":98.33,
    "BOS":101.33,
    "CIN":100.33,
    "COL":105.67,
    "KC":100.33,
    "KCR":100.33,
    "DET":100.67,
    "MIN":100.33,
    "CHA":101.33,
    "CHW":101.33,
    "CWS":101.33,
    "NYA":101,
    "NYY":101,
    "NONE":100,
    "":100,
}

def process(year):
    # calculate_war(year)

    for year in range(2011,2017):
        calculate_war(year)


def get_league_avg(year, category):
    yr = year - 1
    q = """SELECT
r,
gs,
era,
era as fip,
fip_const
FROM processed_league_averages_pitching
WHERE year = %s
"""
    qry = q % yr
    query = db.query(qry)[0]
    lg_r, lg_gs, lg_era, lg_fip, fip_const = query
    avgs = {"lg_r":lg_r, "lg_gs":lg_gs, "lg_era":lg_era, "lg_fip":lg_fip, "fip_const":fip_const}

    return avgs.get(category)


def get_pitching_metrics(metric_9, ip, year, pf,  g, gs, _type):
    park_metric = metric_9/pf

    search_metric = 'lg_' + _type
    lg_metric = float(get_league_avg(year,search_metric))
    metric_min = 100*(park_metric/lg_metric)

    RApxMETRIC = float(park_metric)/0.92

    lg_r = float(get_league_avg(year,'lg_r'))
    lg_gs = float(get_league_avg(year,'lg_gs'))
    metric_RE = ((((18-(float(ip)/float(g)))*(float(lg_r)/float(lg_gs))+(float(ip)/float(g))*RApxMETRIC)/18)+2)*1.5

    if (float(gs)/float(g)) > 0.5:
        METRIC_x_win = ((lg_metric-RApxMETRIC)/(metric_RE))+0.5
        METRIC_x_win_9 = METRIC_x_win - 0.38
    else:
        METRIC_x_win = ((lg_metric-RApxMETRIC)/(metric_RE))+0.52
        METRIC_x_win_9 = METRIC_x_win - 0.46

    METRIC_WAR = METRIC_x_win_9*float(ip)/9.0

    return park_metric, metric_min, METRIC_WAR




def calculate_war(year):
    player_q = """SELECT
player_name,
team_abb,
g, 
gs,
era,
ip,
h, r, er, bb, so, hr
FROM zips_pitching_%s
"""
    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        player_name, team_abb, g, gs, era, ip, h, r, er, bb, k, hr = row


        team_abb = team_abb.upper()
        pf = float(park_factors.get(team_abb))/float(100)

        if ip == 0:
            k_9 = 0.0
            if bb > 0:
                bb_9 = 99.0
                k_bb = 99.0
            else:
                bb_9 = 0.0
                k_bb = 0.0
            if hr > 0:
                hr_9 = 99.0
            else:
                hr_9 = 0.0
        else:
            k_9 = (float(k)/float(ip))*9
            bb_9 = (float(bb)/float(ip))*9
            hr_9 = (float(hr)/float(ip))*9
            if bb == 0:
                if k > 0:
                    k_bb = 99.0
                else:
                    k_bb = 0.0
            else:
                k_bb = (float(k)/float(bb))


        fip_const = float(get_league_avg(year,'fip_const'))
        FIP = ((((13*float(hr))+(3*float(bb))-(2*float(k)))/float(ip))+fip_const)
        park_FIP, FIP_min, FIP_WAR = get_pitching_metrics(FIP, ip, year, pf, g, gs, 'fip')

        ERA = float(era)
        park_ERA, ERA_min, ERA_WAR = get_pitching_metrics(ERA, ip, year, pf, g, gs, 'era')

        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['pf'] = pf
        entry['ip'] = ip
        entry['k_9'] = k_9
        entry['bb_9'] = bb_9
        entry['k_bb'] = k_bb
        entry['hr_9'] = hr_9
        entry['FIP'] = FIP
        entry['park_FIP'] = park_FIP
        entry['FIP_minus'] = FIP_min
        entry['FIP_WAR'] = FIP_WAR
        entry['ERA'] = era
        entry['park_ERA'] = park_ERA
        entry['ERA_minus'] = ERA_min
        entry['ERA_WAR'] = ERA_WAR

        entries.append(entry)


    table = 'zips_processed_WAR_pitchers_%s' % year
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()



if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2012)
    args = parser.parse_args()
    
    process(args.year)
