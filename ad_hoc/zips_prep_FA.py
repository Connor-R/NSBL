from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time


db = db('NSBL')

# find potential FA

# SELECT f.year
# , f.player_name
# , c.age
# , f.team_abb
# , f.pos
# , f.zOPS_Plus
# , f.DEF
# , f.wRC_plus
# , f.WAR600
# FROM zips_fangraphs_prep_FA_batters f
# JOIN zips_fangraphs_batters_counting c on (f.year=c.year AND f.player_name=c.player AND f.team_abb=c.team_abb)
# LEFT JOIN(
#     SELECT *
#     FROM excel_rosters
#     JOIN (
#         SELECT year
#         , MAX(gp) AS gp
#         FROM excel_rosters
#         WHERE 1
#             AND year = 2020
#     ) cur USING (year, gp)
# ) r ON (f.player_name=r.player_name)
# where r.player_name is null
# and c.age >= 25
# and c.team_abb IN ('COL')
# and f.year = 2020
# order by f.war600 desc
# ;

# SELECT f.year
# , f.player_name
# , c.age
# , f.team_abb
# , f.pos
# , f.ip
# , f.zERA_plus
# , f.zERA_minus
# , f.zWAR
# , f.k_9
# , f.bb_9
# , f.k_bb
# , f.hr_9
# , f.FIP_minus
# , f.ERA_minus
# , f.FIP_WAR
# , f.ERA_WAR
# FROM zips_fangraphs_prep_FA_pitchers f
# JOIN zips_fangraphs_pitchers_counting c on (f.year=c.year AND f.player_name=c.player AND f.team_abb=c.team_abb)
# LEFT JOIN(
#     SELECT *
#     FROM excel_rosters
#     JOIN (
#         SELECT year
#         , MAX(gp) AS gp
#         FROM excel_rosters
#         WHERE 1
#             AND year = 2020
#     ) cur USING (year, gp)
# ) r ON (f.player_name=r.player_name)
# where r.player_name is null
# and c.age >= 25
# and c.team_abb IN ('COL')
# and f.year = 2020
# order by f.FIP_WAR desc
# ;


def process(year):

    batters(year)
    pitchers(year)


def batters(year):
    player_q = """SELECT year
    , Player
    , team_abb
    , age
    , B as hand
    , PO
    , COALESCE(a.PA, c.PA) AS pa
    , ab
    , h
    , 2b
    , 3b
    , hr
    , bb
    , so
    , sb
    , cs
    , BA
    , OBP
    , SLG
    , BABIP
    , OPS_Plus
    , DEF
    , WAR
    FROM zips_fangraphs_batters_counting a
    JOIN(
        SELECT year
        , Player
        , MAX(post_date) AS post_date
        FROM zips_fangraphs_batters_counting
        WHERE 1
            AND year = %s
        GROUP BY year, Player
    ) b USING (year,Player,post_date)
    JOIN zips_fangraphs_batters_rate c USING (year, Player, team_abb)
    """
    player_qry = player_q % (year)
    # raw_input(player_qry)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        year, player_name, team_abb, age, hand, po, pa, ab, h, _2, _3, hr, bb, so, sb, cs, ba, obp, slg, babip, zOPS_Plus, DEF, WAR = row

        if pa is None:
            pa = ab+bb
        bb2 = bb
        hbp = 0
        _1 = h - _2 - _3 - hr

        team_abb = team_abb.upper()

        pf = float(helper.get_park_factors(team_abb))/float(100)

        WAR600 = 600*(float(WAR)/float(pa))


        ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR = helper.get_zips_offensive_metrics(year-1, pf, pa, ab, bb2, hbp, _1, _2, _3, hr, sb, cs)

        entry['year'] = year
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['age'] = age
        entry['hand'] = hand
        entry['pos'] = po
        entry['pf'] = pf
        entry['pa'] = pa
        entry['ba'] = ba
        entry['obp'] = obp
        entry['slg'] = slg
        entry['zOPS_Plus'] = zOPS_Plus
        entry['DEF'] = DEF
        entry['zWAR'] = WAR
        entry['babip'] = babip
        entry['OPS_plus'] = OPS_plus
        entry['park_wOBA'] = park_wOBA
        entry['wRC_plus'] = wRC_plus
        entry['WAR600'] = WAR600

        entries.append(entry)


    table = 'zips_fangraphs_prep_FA_batters'
    print table
    if entries != []:
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i: i + 1000], table, insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


def pitchers(year):
    player_q = """SELECT year
    , Player
    , team_abb
    , age
    , T as hand
    , ERA
    , G
    , GS
    , IP
    , H
    , ER
    , HR
    , BB
    , SO
    , k_9
    , bb_9
    , hr_9
    , bb_pct
    , k_pct
    , BABIP
    , ERA_Plus
    , ERA_minus
    , COALESCE(a.FIP, c.FIP) AS FIP
    , WAR
    FROM zips_fangraphs_pitchers_counting a
    JOIN(
        SELECT year
        , Player
        , MAX(post_date) AS post_date
        FROM zips_fangraphs_pitchers_counting
        WHERE 1
            AND year = %s
        GROUP BY year, Player
    ) b USING (year,Player,post_date)
    JOIN zips_fangraphs_pitchers_rate c USING (year, Player, team_abb)
    """
    player_qry = player_q % (year)
    # raw_input(player_qry)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        year, player_name, team_abb, age, hand, era, g, gs, ip, h, er, hr, bb, k, k_9, bb_9, hr_9, bb_pct, k_pct, babip, zera_plus, zera_minus, zfip, zwar = row

        r = er
        if (gs >= 10 or float(gs)/float(g) > 0.4):
            pos = 'SP'
        else:
            pos = 'RP'

        team_abb = team_abb.upper()

        pf = float(helper.get_park_factors(team_abb))/float(100)

        if float(bb) == 0:
            if float(k) > 0:
                k_bb = 99.0
            else:
                k_bb = 0.0
        else:
            k_bb = (float(k)/float(bb))


        fip_const = float(helper.get_zips_average_pitchers(year-1, 'fip_const'))
        FIP = ((((13*float(hr))+(3*float(bb))-(2*float(k)))/float(ip))+fip_const)
        park_FIP, FIP_min, FIP_WAR = helper.get_zips_pitching_metrics(FIP, ip, year-1, pf, g, gs, 'fip')

        ERA = float(era)
        park_ERA, ERA_min, ERA_WAR = helper.get_zips_pitching_metrics(ERA, ip, year-1, pf, g, gs, 'era')

        if pos == 'SP':
            FIP_WAR = 180*(float(FIP_WAR)/float(ip))
            ERA_WAR = 180*(float(ERA_WAR)/float(ip))
        elif pos == 'RP':
            FIP_WAR = 60*(float(FIP_WAR)/float(ip))
            ERA_WAR = 60*(float(ERA_WAR)/float(ip))

        k_minus_bb_pct = float(k_pct)-float(bb_pct)  

        entry['year'] = year
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['age'] = age
        entry['hand'] = hand
        entry['pos'] = pos
        entry['pf'] = pf
        entry['ip'] = ip
        entry['babip'] = babip
        entry['k_9'] = k_9
        entry['bb_9'] = bb_9
        entry['k_bb'] = k_bb
        entry['hr_9'] = hr_9
        entry['k_pct'] = k_pct
        entry['bb_pct'] = bb_pct
        entry['k_minus_bb_pct'] = k_minus_bb_pct
        entry['zERA_plus'] = zera_plus
        entry['zERA_minus'] = zera_minus
        entry['zFIP'] = zfip
        entry['zWAR'] = zwar
        entry['FIP'] = FIP
        entry['park_FIP'] = park_FIP
        entry['FIP_minus'] = FIP_min
        entry['FIP_WAR'] = FIP_WAR
        entry['ERA'] = era
        entry['park_ERA'] = park_ERA
        entry['ERA_minus'] = ERA_min
        entry['ERA_WAR'] = ERA_WAR

        entries.append(entry)

    table = 'zips_fangraphs_prep_FA_pitchers'
    print table
    if entries != []:
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i: i + 1000], table, insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()

    parser.add_argument("--year",type=int,default=2020)
    args = parser.parse_args()
    
    process(args.year)


