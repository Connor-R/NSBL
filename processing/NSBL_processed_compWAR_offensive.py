from py_db import db
import argparse
from decimal import Decimal


# Calculates the offense only portion of WAR for every player in a years hitting register.


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
    offensive_war(year)

    if year >= 2017:
        multi_team_war(year)


def get_league_avg(year, category):
    q = """SELECT
pa,
r,
(h+bb+hbp)/pa as obp,
(1b + 2*2b + 3*3b + 4*hr)/ab as slg,
woba
FROM processed_league_averages_hitting
WHERE year = %s
"""
    qry = q % year
    query = db.query(qry)[0]
    lg_pa, lg_r, lg_obp, lg_slg, lg_woba = query
    avgs = {"lg_pa":lg_pa, "lg_r":lg_r, "lg_obp":lg_obp, "lg_slg":lg_slg, "lg_woba":lg_woba}

    return avgs.get(category)


def get_offensive_metrics(year, pf, pa, ab, bb, hbp, _1b, _2b, _3b, hr, sb, cs):
    wOBA = ((0.691*bb + 0.722*hbp + 0.884*_1b + 1.257*_2b + 1.593*_3b + 2.058*hr + 0.2*sb - 0.398*cs)/(pa))
    
    park_wOBA = wOBA/pf
    
    h = _1b + _2b + _3b + hr 
    if pa != 0:
        obp = (h + bb + hbp)/float(pa)
    else:
        obp = 0.0
    if ab != 0:
        slg = (_1b + 2*_2b + 3*_3b + 4*hr)/float(ab)
    else:
        slg = 0.0

    ops = obp+slg
    lg_obp = float(get_league_avg(year,'lg_obp'))
    lg_slg = float(get_league_avg(year,'lg_slg'))
    OPS_plus = 100*(((obp/pf)/lg_obp)+((slg/pf)/lg_slg)-1)

    lg_woba = float(get_league_avg(year,'lg_woba'))
    lg_r = float(get_league_avg(year,'lg_r'))
    lg_pa = float(get_league_avg(year,'lg_pa'))
    wrc = (((park_wOBA-lg_woba)/1.15)+(lg_r/lg_pa))*pa

    if (ab-h) != 0:
        wrc27 = wrc*27/(ab-h)
    else:
        wrc27 = 0.0

    wRC_plus = ((wrc/pa/(lg_r/lg_pa)*100))

    raa = pa*((park_wOBA-lg_woba)/1.25)

    oWAR = raa/10

    return ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR


def offensive_war(year):
    player_q = """SELECT
player_name,
team_abb,
position,
age,
pa,
ab,
(h-2b-3b-hr) as 1b, 2b, 3b, hr, r, rbi, bb, k, hbp, sb, cs, ops, babip
FROM register_batting_primary
JOIN register_batting_secondary USING (year, player_name, team_abb, position, age)
JOIN register_batting_analytical USING (year, player_name, team_abb, position, age)
WHERE year = %s
"""
    player_qry = player_q % (year)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        entry['year'] = year
        player_name, team_abb, position, age, pa, ab, _1b, _2b, _3b, hr, r, rbi, bb, k, hbp, sb, cs, ops, babip = row
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['position'] = position
        if player_name[len(player_name)-1:] == "*":
            bats = 'l'
        elif player_name[len(player_name)-1:] == "#":
            bats = 's'
        else:
            bats = 'r'
        entry['bats'] = bats
        
        entry['age'] = age

        entry['pa'] = pa

        team_abb = team_abb.upper()
        pf = float(park_factors.get(team_abb))/float(100)
        entry['pf'] = pf
        entry['ops'] = ops
        entry['babip'] = babip


        foo, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR = get_offensive_metrics(year, pf, pa, ab, bb, hbp, _1b, _2b, _3b, hr, sb, cs)

        entry['wOBA'] = wOBA
        entry['park_wOBA'] = park_wOBA
        entry['OPS_plus'] = OPS_plus
        entry['wrc'] = wrc
        entry['wRC_27'] = wrc27
        entry['wRC_plus'] = wRC_plus
        entry['raa'] = raa
        entry['oWAR'] = oWAR

        entries.append(entry)


    table = 'processed_compWAR_offensive'
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()




if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2016)
    args = parser.parse_args()
    
    process(args.year)
    