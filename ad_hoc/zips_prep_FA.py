from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time


db = db('NSBL')

# find potential FA

# SELECT * FROM zips_fangraphs_prep_FA_batters WHERE year = 2020;
# SELECT * FROM zips_fangraphs_prep_FA_pitchers WHERE year = 2020;
# SELECT b.*
# FROM(
#     SELECT *
#     FROM(
#         SELECT f.player_name
#         /* , f.year
#         , c.age
#         , f.team_abb
#         , f.pos
#         , f.zOPS_Plus
#         , f.DEF
#         , f.wRC_plus
#         , f.scaledWAR */
#         FROM zips_fangraphs_prep_FA_batters f
#         JOIN zips_fangraphs_batters_counting c on (f.year=c.year AND f.player_name=c.player AND f.team_abb=c.team_abb)
#         LEFT JOIN(
#             SELECT *
#             FROM excel_rosters
#             JOIN (
#                 SELECT year
#                 , MAX(gp) AS gp
#                 FROM excel_rosters
#                 WHERE 1
#                     AND year = 2020
#             ) cur USING (year, gp)
#         ) r ON (f.player_name=r.player_name)
#         where r.player_name is null
#         and c.age >= 25
#         -- and c.team_abb IN ('COL')
#         and f.year = 2020
#         and ( (600*f.def/f.pa) > 6 or f.zops_plus >= 80 or f.scaledWAR >= 1 or f.wrc_plus >= 80)
#         -- order by f.scaledWAR DESC
#         union
#         select distinct player_name
#         from excel_rosters
#         where 1
#             and year = 2019
#             and position != 'p'
#             and (contract_year = '6th'
#                 or (expires = 2019 and opt = '')
#             )
#     ) a
#     UNION ALL
#     SELECT *
#     FROM(
#         SELECT f.player_name
#         /* , f.year
#         , c.age
#         , f.team_abb
#         , f.pos
#         , f.ip
#         , f.zERA_plus
#         , f.zERA_minus
#         , f.zWAR
#         , f.k_9
#         , f.bb_9
#         , f.k_bb
#         , f.hr_9
#         , f.FIP_minus
#         , f.ERA_minus
#         , f.FIP_WAR
#         , f.ERA_WAR */
#         FROM zips_fangraphs_prep_FA_pitchers f
#         JOIN zips_fangraphs_pitchers_counting c on (f.year=c.year AND f.player_name=c.player AND f.team_abb=c.team_abb)
#         LEFT JOIN(
#             SELECT *
#             FROM excel_rosters
#             JOIN (
#                 SELECT year
#                 , MAX(gp) AS gp
#                 FROM excel_rosters
#                 WHERE 1
#                     AND year = 2020
#             ) cur USING (year, gp)
#         ) r ON (f.player_name=r.player_name)
#         where r.player_name is null
#         and c.age >= 25
#         -- and c.team_abb IN ('COL')
#         and f.year = 2020
#         and if(f.gs >= 3, zERA_plus >= 90, zERA_plus >= 100)
#         -- order by f.FIP_WAR DESC
#         union
#         select distinct replace(player_name,'  ', ' ')
#         from excel_rosters
#         where 1
#             and year = 2019
#             and position = 'p'
#             and (contract_year = '6th'
#                 or (expires = 2019 and opt = '')
#             )
#     ) a
# ) b
# WHERE 1
#     AND player_name NOT IN ('Randy Dobnak', 'Kwang-hyun Kim', 'Sam Delaplane', 'Addison Russ', 'Bennett Sousa', 'Connor Brogdon', 'Corbin Clouse', 'Trevor Bettencourt', 'David Bednar', 'Ethan DeCaster', 'Evan Miller', 'Gabriel Moya', 'Ian Hamilton', 'Joel Kuhnel',  'Wyatt Mills',  'Marcel Renteria',  'Matt Foster',  'Nolan Blackwood', 'Phillip Diehl',  'Will Vest', 'Cole Stapler', 'Garrett Williams', 'Griffin Jax',  'Jeremy Walker',  'Michael King',  'Zack Kelly', 'John Schreiber', 'Kevin Ginkel', 'Miguel Sanchez', 'Jack Anderson', 'Penn Murfee', 'Will D. Smith', 'Shogo Akiyama', 'Brian Serven', 'Ivan Castillo', 'Jon Rosoff', 'Jonathan Morales', 'Arden Pabst', 'Ben DeLuzio', 'Thomas Milone', 'Chas McCormick', 'Danny Woodrow', 'Josh VanMeter', 'Rodrigo Orozco', 'Ryan Grotjohn', 'Vance Vizcaino', 'Jaylin Davis', 'Jake Fraley', 'Hunter Owen', 'Renae Martinez', 'Cole Billingsley', 'Jimmy Kerrigan', 'Chad Sedio', 'Josh Rojas', 'Luke Burch', 'Zach Reks', 'Alfredo Rodriguez', 'Jose Rojas', 'Robel Garcia', 'Tyler Zuber', 'Aaron Civale', 'Logan Ice', 'Zack Short', 'Wyatt Short', 'Daniel Castano', 'Dylan Lee', 'Sterling Sharp', 'Tommy Eveld', 'Alex Dunlap', 'Jonah Heim', "Riley O'Brien", 'Santiago Espinal', 'Tyler Zombro', 'Michael Brosseau', 'Shun Yamaguchi', 'Yoshitomo Tsutsugo', 'Yadiel Hernandez')
# ORDER BY player_name ASC
# ;

# SELECT a.*
# , IF(opt = 'no', NULL, IF(base_value-base_salary > opt_value-opt_salary, 'no', 'yes')) as proj_opt
# , ROUND(IF(opt = 'no', base_salary, IF(base_value-base_salary > opt_value-opt_salary, base_salary, opt_salary)), 3) as proj_salary
# , ROUND(IF(opt = 'no', base_value-base_salary, IF(base_value-base_salary > opt_value-opt_salary, base_value-base_salary, opt_value-opt_salary)), 3) as proj_value
# , ROUND(IF(opt = 'no', base_WAR, IF(base_value-base_salary > opt_value-opt_salary, base_WAR, opt_WAR)), 1) as proj_WAR
# FROM(
#     SELECT hfa.year
#     , hfa.player_name as player
#     , hfa.signing_team as team
#     , hfa.age
#     , hfa.position
#     , hfa.day
#     , hfa.contract_years AS yrs
#     , hfa.opt
#     , hfa.aav
#     , hfa.zWAR
#     , fab.yr1_WAR AS ModelWAR
#     , IF(hfa.opt = 'no', hfa.contract_years*hfa.aav, hfa.contract_years*hfa.aav + 0.1*hfa.aav) AS base_salary
#     , IF(hfa.opt = 'yes', (hfa.contract_years+1)*hfa.aav, NULL) AS opt_salary
#     , CASE 
#         WHEN hfa.contract_years = 1
#             THEN fab.yr1_value 
#         WHEN hfa.contract_years = 2
#             THEN fab.yr2_value 
#         WHEN hfa.contract_years = 3
#             THEN fab.yr3_value 
#         WHEN hfa.contract_years = 4
#             THEN fab.yr4_value 
#         WHEN hfa.contract_years = 5
#             THEN fab.yr5_value 
#         WHEN hfa.contract_years = 6
#             THEN fab.yr6_value 
#         WHEN hfa.contract_years = 7
#             THEN fab.yr7_value 
#     END AS base_value
#     , CASE WHEN hfa.opt = 'no'
#         THEN NULL
#         ELSE CASE
#             WHEN hfa.contract_years = 1
#                 THEN fab.yr2_value 
#             WHEN hfa.contract_years = 2
#                 THEN fab.yr3_value 
#             WHEN hfa.contract_years = 3
#                 THEN fab.yr4_value 
#             WHEN hfa.contract_years = 4
#                 THEN fab.yr5_value 
#             WHEN hfa.contract_years = 5
#                 THEN fab.yr6_value 
#             WHEN hfa.contract_years = 6
#                 THEN fab.yr7_value 
#             WHEN hfa.contract_years = 7
#                 THEN fab.yr8_value 
#         END END AS opt_value
#     , CASE 
#         WHEN hfa.contract_years = 1
#             THEN fab.yr1_WAR
#         WHEN hfa.contract_years = 2
#             THEN fab.yr2_WAR
#         WHEN hfa.contract_years = 3
#             THEN fab.yr3_WAR
#         WHEN hfa.contract_years = 4
#             THEN fab.yr4_WAR
#         WHEN hfa.contract_years = 5
#             THEN fab.yr5_WAR
#         WHEN hfa.contract_years = 6
#             THEN fab.yr6_WAR
#         WHEN hfa.contract_years = 7
#             THEN fab.yr7_WAR
#     END AS base_WAR
#     , CASE WHEN hfa.opt = 'no'
#         THEN NULL
#         ELSE CASE
#             WHEN hfa.contract_years = 1
#                 THEN fab.yr2_WAR
#             WHEN hfa.contract_years = 2
#                 THEN fab.yr3_WAR
#             WHEN hfa.contract_years = 3
#                 THEN fab.yr4_WAR
#             WHEN hfa.contract_years = 4
#                 THEN fab.yr5_WAR
#             WHEN hfa.contract_years = 5
#                 THEN fab.yr6_WAR
#             WHEN hfa.contract_years = 6
#                 THEN fab.yr7_WAR
#             WHEN hfa.contract_years = 7
#                 THEN fab.yr8_WAR
#         END END AS opt_WAR
#     FROM historical_free_agency hfa
#     LEFT JOIN zips_fangraphs_prep_FA_batters fab ON (hfa.player_name = fab.player_name
#         AND hfa.year = fab.year
#     )
#     WHERE 1
#         AND hfa.year = 2019
#         AND hfa.position NOT IN ('RP', 'SP')
#     UNION ALL   
#     SELECT hfa.year
#     , hfa.player_name
#     , hfa.signing_team
#     , hfa.age
#     , hfa.position
#     , hfa.day
#     , hfa.contract_years
#     , hfa.opt
#     , hfa.aav
#     , hfa.zWAR
#     , fab.yr1_WAR AS ModelWAR
#     , IF(hfa.opt = 'no', hfa.contract_years*hfa.aav, hfa.contract_years*hfa.aav + 0.1*hfa.aav) AS base_salary
#     , IF(hfa.opt = 'yes', (hfa.contract_years+1)*hfa.aav, NULL) AS opt_salary
#     , CASE 
#         WHEN hfa.contract_years = 1
#             THEN fab.yr1_value 
#         WHEN hfa.contract_years = 2
#             THEN fab.yr2_value 
#         WHEN hfa.contract_years = 3
#             THEN fab.yr3_value 
#         WHEN hfa.contract_years = 4
#             THEN fab.yr4_value 
#         WHEN hfa.contract_years = 5
#             THEN fab.yr5_value 
#         WHEN hfa.contract_years = 6
#             THEN fab.yr6_value 
#         WHEN hfa.contract_years = 7
#             THEN fab.yr7_value 
#     END AS base_value
#     , CASE WHEN hfa.opt = 'no'
#         THEN NULL
#         ELSE CASE
#             WHEN hfa.contract_years = 1
#                 THEN fab.yr2_value 
#             WHEN hfa.contract_years = 2
#                 THEN fab.yr3_value 
#             WHEN hfa.contract_years = 3
#                 THEN fab.yr4_value 
#             WHEN hfa.contract_years = 4
#                 THEN fab.yr5_value 
#             WHEN hfa.contract_years = 5
#                 THEN fab.yr6_value 
#             WHEN hfa.contract_years = 6
#                 THEN fab.yr7_value 
#             WHEN hfa.contract_years = 7
#                 THEN fab.yr8_value 
#         END END AS opt_value
#     , CASE 
#         WHEN hfa.contract_years = 1
#             THEN fab.yr1_WAR
#         WHEN hfa.contract_years = 2
#             THEN fab.yr2_WAR
#         WHEN hfa.contract_years = 3
#             THEN fab.yr3_WAR
#         WHEN hfa.contract_years = 4
#             THEN fab.yr4_WAR
#         WHEN hfa.contract_years = 5
#             THEN fab.yr5_WAR
#         WHEN hfa.contract_years = 6
#             THEN fab.yr6_WAR
#         WHEN hfa.contract_years = 7
#             THEN fab.yr7_WAR
#     END AS base_WAR
#     , CASE WHEN hfa.opt = 'no'
#         THEN NULL
#         ELSE CASE
#             WHEN hfa.contract_years = 1
#                 THEN fab.yr2_WAR
#             WHEN hfa.contract_years = 2
#                 THEN fab.yr3_WAR
#             WHEN hfa.contract_years = 3
#                 THEN fab.yr4_WAR
#             WHEN hfa.contract_years = 4
#                 THEN fab.yr5_WAR
#             WHEN hfa.contract_years = 5
#                 THEN fab.yr6_WAR
#             WHEN hfa.contract_years = 6
#                 THEN fab.yr7_WAR
#             WHEN hfa.contract_years = 7
#                 THEN fab.yr8_WAR
#         END END AS opt_WAR
#     FROM historical_free_agency hfa
#     LEFT JOIN zips_fangraphs_prep_FA_pitchers fab ON (hfa.player_name = fab.player_name
#         AND hfa.year = fab.year
#     )
#     WHERE 1
#         AND hfa.year = 2019
#         AND hfa.position IN ('RP', 'SP')
# ) a
# ORDER BY proj_value DESC
# ;


def process(year):

    clear_year = "DELETE FROM zips_fangraphs_prep_FA_batters WHERE year = %s;" % (year)
    db.query(clear_year)
    db.conn.commit()
    batters(year)

    clear_year = "DELETE FROM zips_fangraphs_prep_FA_pitchers WHERE year = %s;" % (year)
    db.query(clear_year)
    db.conn.commit()
    pitchers(year)


def batters(year):



    player_q = """SELECT a.year
    , IFNULL(CONCAT(nm.right_fname, ' ', nm.right_lname), a.Player) AS player
    , a.team_abb
    , a.age
    , a.B as hand
    , a.PO
    , COALESCE(a.PA, c.PA) AS pa
    , a.ab
    , a.h
    , a.2b
    , a.3b
    , a.hr
    , a.bb
    , a.so
    , a.sb
    , a.cs
    , BA
    , OBP
    , SLG
    , BABIP
    , OPS_Plus
    , DEF
    , c.WAR
    , cv.yr1_WAR
    , cv.yr1_value
    , cv.yr2_WAR
    , cv.yr2_value
    , cv.yr3_WAR
    , cv.yr3_value
    , cv.yr4_WAR
    , cv.yr4_value
    , cv.yr5_WAR
    , cv.yr5_value
    , cv.yr6_WAR
    , cv.yr6_value
    , cv.yr7_WAR
    , cv.yr7_value
    , cv.yr8_WAR
    , cv.yr8_value
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
    LEFT JOIN name_mapper nm ON (1
        AND a.Player = nm.wrong_name
        AND (nm.start_year IS NULL OR nm.start_year <= a.year)
        AND (nm.end_year IS NULL OR nm.end_year >= a.year)
        AND (nm.position = '' OR nm.position = a.PO)
        AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
        # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
    )
    LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
        AND nm.right_lname = nm2.right_lname
        AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
        AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
        AND (nm.position = '' OR nm.position = nm2.position)
        AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
    )
    JOIN zips_FA_contract_value_batters cv ON (a.year = cv.year 
        AND a.team_abb = cv.team_abb
        AND IFNULL(nm2.wrong_name, a.Player) = cv.Player
    ) 
    ;"""
    player_qry = player_q % (year)
    # raw_input(player_qry)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        year, player_name, team_abb, age, hand, po, pa, ab, h, _2, _3, hr, bb, so, sb, cs, ba, obp, slg, babip, zOPS_Plus, DEF, WAR, yr1_WAR, yr1_value, yr2_WAR, yr2_value, yr3_WAR, yr3_value, yr4_WAR, yr4_value, yr5_WAR, yr5_value, yr6_WAR, yr6_value, yr7_WAR, yr7_value, yr8_WAR, yr8_value = row

        if pa is None:
            pa = ab+bb
        bb2 = bb
        hbp = 0
        _1 = h - _2 - _3 - hr

        team_abb = team_abb.upper()

        pf = float(helper.get_park_factors(team_abb, year-1))/float(100)

        if po.lower() != 'c':
            scaledWAR = 600*(float(WAR)/float(pa))
        else:
            scaledWAR = 450*(float(WAR)/float(pa))

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
        entry['scaledWAR'] = scaledWAR
        entry['yr1_WAR'] = yr1_WAR
        entry['yr1_value'] = yr1_value
        entry['yr2_WAR'] = yr2_WAR
        entry['yr2_value'] = yr2_value
        entry['yr3_WAR'] = yr3_WAR
        entry['yr3_value'] = yr3_value
        entry['yr4_WAR'] = yr4_WAR
        entry['yr4_value'] = yr4_value
        entry['yr5_WAR'] = yr5_WAR
        entry['yr5_value'] = yr5_value
        entry['yr6_WAR'] = yr6_WAR
        entry['yr6_value'] = yr6_value
        entry['yr7_WAR'] = yr7_WAR
        entry['yr7_value'] = yr7_value
        entry['yr8_WAR'] = yr8_WAR
        entry['yr8_value'] = yr8_value


        entries.append(entry)


    table = 'zips_fangraphs_prep_FA_batters'
    print table
    if entries != []:
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i: i + 1000], table, insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


def pitchers(year):
    player_q = """SELECT a.year
    , IFNULL(CONCAT(nm.right_fname, ' ', nm.right_lname), a.Player) AS player
    , a.team_abb
    , a.age
    , T as hand
    , ERA
    , a.G
    , a.GS
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
    , c.WAR
    , cv.yr1_WAR
    , cv.yr1_value
    , cv.yr2_WAR
    , cv.yr2_value
    , cv.yr3_WAR
    , cv.yr3_value
    , cv.yr4_WAR
    , cv.yr4_value
    , cv.yr5_WAR
    , cv.yr5_value
    , cv.yr6_WAR
    , cv.yr6_value
    , cv.yr7_WAR
    , cv.yr7_value
    , cv.yr8_WAR
    , cv.yr8_value
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
    LEFT JOIN name_mapper nm ON (1
        AND a.Player = nm.wrong_name
        AND (nm.start_year IS NULL OR nm.start_year <= a.year)
        AND (nm.end_year IS NULL OR nm.end_year >= a.year)
        # AND (nm.position = '' OR nm.position = a.PO)
        AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
        # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
    )
    LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
        AND nm.right_lname = nm2.right_lname
        AND (nm.start_year IS NULL OR nm2.start_year = nm2.start_year)
        AND (nm.end_year IS NULL OR nm2.end_year = nm2.end_year)
        AND (nm.position = '' OR nm2.position = nm2.position)
        AND (nm.rl_team = '' OR nm2.rl_team = nm2.rl_team)
    )
    JOIN zips_FA_contract_value_pitchers cv ON (a.year = cv.year 
        AND a.team_abb = cv.team_abb
        AND IFNULL(nm2.wrong_name, a.Player) = cv.Player
    )
    ;"""
    
    player_qry = player_q % (year)
    # raw_input(player_qry)
    player_data = db.query(player_qry)

    entries = []
    for row in player_data:
        entry = {}
        year, player_name, team_abb, age, hand, era, g, gs, ip, h, er, hr, bb, k, k_9, bb_9, hr_9, bb_pct, k_pct, babip, zera_plus, zera_minus, zfip, zwar, yr1_WAR, yr1_value, yr2_WAR, yr2_value, yr3_WAR, yr3_value, yr4_WAR, yr4_value, yr5_WAR, yr5_value, yr6_WAR, yr6_value, yr7_WAR, yr7_value, yr8_WAR, yr8_value = row

        r = er
        if (gs >= 20 or float(gs)/float(g) > 0.8):
            pos = 'SP'
        else:
            pos = 'RP'

        team_abb = team_abb.upper()

        pf = float(helper.get_park_factors(team_abb, year-1))/float(100)

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
            FIP_WAR = 32*(float(FIP_WAR)/float(gs))
            ERA_WAR = 32*(float(ERA_WAR)/float(gs))
        elif pos == 'RP':
            FIP_WAR = float(FIP_WAR)
            ERA_WAR = float(ERA_WAR)

        if k_pct is not None and bb_pct is not None:
            k_minus_bb_pct = float(k_pct)-float(bb_pct)  
        else:
            k_minus_bb_pct = None

        entry['year'] = year
        entry['player_name'] = player_name
        entry['team_abb'] = team_abb
        entry['age'] = age
        entry['hand'] = hand
        entry['pos'] = pos
        entry['pf'] = pf
        entry['g'] = g
        entry['gs'] = gs
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
        entry['yr1_WAR'] = yr1_WAR
        entry['yr1_value'] = yr1_value
        entry['yr2_WAR'] = yr2_WAR
        entry['yr2_value'] = yr2_value
        entry['yr3_WAR'] = yr3_WAR
        entry['yr3_value'] = yr3_value
        entry['yr4_WAR'] = yr4_WAR
        entry['yr4_value'] = yr4_value
        entry['yr5_WAR'] = yr5_WAR
        entry['yr5_value'] = yr5_value
        entry['yr6_WAR'] = yr6_WAR
        entry['yr6_value'] = yr6_value
        entry['yr7_WAR'] = yr7_WAR
        entry['yr7_value'] = yr7_value
        entry['yr8_WAR'] = yr8_WAR
        entry['yr8_value'] = yr8_value

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


