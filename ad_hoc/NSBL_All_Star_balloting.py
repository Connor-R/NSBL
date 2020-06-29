from py_db import db
import argparse
import csv


# Takes in a year and writes out 2 csvs (hitting/pitching) for the primary statistics for all players for that year

db = db('NSBL')


def process(year, path):
    process_hitters(year, path)
    process_pitchers(year, path)


def process_pitchers(year, path):
    query = """SELECT
player_name, a.year,
IF(((career_ip - ip < 30) AND (contract NOT IN ('V','CE','2nd','3rd','4th','5th','6th') OR contract IS NULL)), 'yes', 'no') AS 'ROY_eligible',
league, division, a.team_abb AS main_team, teams,
age,
IF((g/gs)>0.5, 'SP', 'RP') AS primary_role,
ip, w, l, sv, g, gs, cg, sho, h, r, er, bb, k, hr, gdp,
era, fip, k_9, bb_9, k_bb, hr_9,
era_minus, fip_minus, era_WAR, fip_WAR, split_WAR
FROM(
    SELECT 
    YEAR, 
    GROUP_CONCAT(team_abb ORDER BY p.ip DESC SEPARATOR '/') AS teams,
    SUBSTRING_INDEX(GROUP_CONCAT(team_abb ORDER BY p.ip DESC SEPARATOR '/'), '/', 1) AS team_abb,
    player_name, 
    p.age,
    SUM(p.ip) AS ip,
    SUM(w) AS w, 
    SUM(l) AS l, 
    SUM(sv) AS sv, 
    SUM(g) AS g, 
    SUM(gs) AS gs, 
    SUM(cg) AS cg, 
    SUM(sho) AS sho, 
    SUM(h) AS h, 
    SUM(r) AS r, 
    SUM(er) AS er, 
    SUM(bb) AS bb, 
    SUM(k) AS k, 
    SUM(hr) AS hr, 
    SUM(gdp) AS gdp,
    ROUND(SUM(p.ERA*p.ip)/SUM(p.ip),2) AS era, 
    ROUND(SUM(FIP*p.ip)/SUM(p.ip),2) AS fip, 
    ROUND(SUM(k_9*p.ip)/SUM(p.ip),1) AS k_9, 
    ROUND(SUM(bb_9*p.ip)/SUM(p.ip),1) AS bb_9, 
    ROUND(SUM(k_bb*p.ip)/SUM(p.ip),1) AS k_bb, 
    ROUND(SUM(hr_9*p.ip)/SUM(p.ip),1) AS hr_9, 
    ROUND(SUM(ERA_minus*p.ip)/SUM(p.ip),0) AS era_minus, 
    ROUND(SUM(FIP_minus*p.ip)/SUM(p.ip),0) AS fip_minus, 
    ROUND(SUM(era_war),1) AS era_war,
    ROUND(SUM(fip_war),1) AS fip_WAR,
    ROUND((era_war+fip_war)/2,1) AS 'split_WAR'
    FROM processed_WAR_pitchers p
    JOIN register_pitching_primary b USING (YEAR, player_name, team_abb)
    GROUP BY YEAR, player_name
    ORDER BY fip_war DESC
)a
LEFT JOIN (SELECT team_abb, division, LEFT(division,2) AS league FROM __playoff_probabilities GROUP BY team_name) b USING (team_abb)
LEFT JOIN (SELECT player_name, ip AS 'career_ip' FROM historical_stats_pitchers_advanced) c USING (player_name)
LEFT JOIN(
    SELECT player_name
    , contract_year as 'contract'

    FROM excel_rosters
    JOIN (
        SELECT year
        , MAX(gp) AS gp
        FROM excel_rosters
        WHERE 1
            AND year = %s
    ) cur USING (year, gp)
) d USING (player_name)
WHERE a.year = %s
ORDER BY YEAR DESC, split_WAR DESC;"""

    query = query % (year, year)
    res = db.query(query)

    csv_title = path + str(year) + '_Pitchers.csv'
    csv_file = open(csv_title, 'wb')
    append_csv = csv.writer(csv_file)
    csv_header = ['player_name', 'year', 'roy_eligible', 'league', 'division', 'primary_team', 'all_teams', 'age', 'primary_role', 'ip', 'w', 'l', 'sv', 'g', 'gs', 'cg', 'sho', 'h', 'r', 'er', 'bb', 'k', 'hr', 'gdp', 'ERA', 'FIP', 'K/9', 'BB/9', 'K/BB', 'HR/9', 'ERA-', 'FIP-', 'ERA_WAR', 'FIP_WAR', 'split_WAR']
    append_csv.writerow(csv_header)

    for row in res:
        append_csv.writerow(row)





def process_hitters(year, path):
    query = """SELECT
player_name, a.year,
IF(((career_pa - pa < 120) AND (contract NOT IN ('V','CE','2nd','3rd','4th','5th','6th') OR contract IS NULL)), 'yes', 'no') AS 'ROY_eligible',
league, division, a.team_abb AS main_team, teams,
age, 
main_position, positions, defensive_innings,
pa, ab, h, 2b, 3b, hr, r, rbi, hbp, bb, k, sb, cs,
bb_pct, k_pct, iso, BABIP, wOBA, OPS_plus, wRC_plus,
0 AS DRS, position_adj, dWAR,
oWAR,
replacement,
noD_WAR
FROM(
    SELECT
    YEAR,
    GROUP_CONCAT(team_abb ORDER BY pa DESC SEPARATOR '/') AS teams, 
    SUBSTRING_INDEX(GROUP_CONCAT(team_abb ORDER BY pa DESC SEPARATOR '/'), '/', 1) AS team_abb,
    player_name, age, positions, 
    SUBSTRING_INDEX(positions, '/', 1) AS main_position,
    SUM(defensive_innings) AS defensive_innings,
    SUM(w.pa) AS pa,
    SUM(ab) AS ab,
    SUM(h) AS h,
    SUM(2b) AS 2b,
    SUM(3b) AS 3b,
    SUM(hr) AS hr,
    SUM(r) AS r,
    SUM(rbi) AS rbi,
    SUM(hbp) AS hbp,
    SUM(bb) AS bb,
    SUM(k) AS k,
    SUM(sb) AS sb,
    SUM(cs) AS cs,
    ROUND(SUM((100*bb/w.pa)*(ab+bb+hbp))/SUM((ab+bb+hbp)),1) AS 'bb_pct',
    ROUND(SUM((100*k/ab)*(ab+bb+hbp))/SUM((ab+bb+hbp)),1) AS 'k_pct',
    ROUND(SUM((slg-AVG)*(ab+bb+hbp))/SUM((ab+bb+hbp)),3) AS 'iso',
    ROUND(SUM(babip*(ab+bb+hbp))/SUM((ab+bb+hbp)),3) AS 'babip',
    ROUND(SUM(park_woba*(ab+bb+hbp))/SUM((ab+bb+hbp)),3) AS 'woba',
    ROUND(SUM(OPS_plus*pa)/SUM(pa),0) AS OPS_plus, ROUND(SUM(wRC_plus*pa)/SUM(pa),0) AS wRC_plus, 
    ROUND(SUM(0),0) AS DRS, ROUND(SUM(position_adj),0) AS position_adj, ROUND(SUM(position_adj/10),1) AS dWAR,
    ROUND(SUM(oWAR),1) AS oWAR,
    ROUND(SUM(replacement),1) AS replacement,
    ROUND(SUM(WAR-defense/10),1) AS noD_WAR,
    ROUND(SUM(WAR),1) AS WAR
    FROM processed_WAR_hitters w
    JOIN processed_compWAR_offensive USING (YEAR, player_name, team_abb, age, position, pa, oWAR)
    JOIN register_batting_primary USING (YEAR, player_name, team_abb, age, position)
    JOIN(
        SELECT 
        YEAR, player_name, team_abb, SUM(inn) AS defensive_innings,
        IF(
            (o.pa/600)*162/(SUM(inn)/9)<1.2,
            GROUP_CONCAT(d.position ORDER BY inn DESC SEPARATOR '/'),
            IF(
                (o.pa/600)*162/(SUM(inn)/9)>2.0,
                CONCAT('dh/', GROUP_CONCAT(d.position ORDER BY inn DESC SEPARATOR '/')),
                CONCAT(GROUP_CONCAT(d.position ORDER BY inn DESC SEPARATOR '/'), '/dh')
            )
        ) AS positions
        FROM processed_compWAR_defensive d
        JOIN processed_compWAR_offensive o USING (YEAR, team_abb, player_name)
        GROUP BY player_name, YEAR, team_abb
    ) d USING (YEAR, player_name, team_abb)
    GROUP BY YEAR, player_name
) a
LEFT JOIN (SELECT team_abb, division, LEFT(division,2) AS league FROM __playoff_probabilities GROUP BY team_name) b USING (team_abb)
LEFT JOIN (SELECT player_name, pa AS 'career_pa' FROM historical_stats_hitters_advanced) c USING (player_name)
LEFT JOIN(
    SELECT player_name
    , contract_year as 'contract'

    FROM excel_rosters
    JOIN (
        SELECT year
        , MAX(gp) AS gp
        FROM excel_rosters
        WHERE 1
            AND year = %s
    ) cur USING (year, gp)
) d USING (player_name)
WHERE a.year = %s
ORDER BY YEAR DESC, noD_WAR DESC;"""

    query = query % (year, year)
    # raw_input(query)
    res = db.query(query)

    csv_title = path + str(year) + '_Hitters.csv'
    csv_file = open(csv_title, 'wb')
    append_csv = csv.writer(csv_file)
    csv_header = ['player_name', 'year', 'roy_eligible', 'league', 'division', 'primary_team', 'all_teams', 'age', 'primary_position', 'all_positions', 'defensive_innings', 'pa', 'ab', 'h', '2b', '3b', 'hr', 'r', 'rbi', 'hbp', 'bb', 'k', 'sb', 'cs', 'BB%', 'K%', 'ISO', 'BABIP', 'wOBA', 'OPS+', 'wRC+', 'DRS', 'positional_adjustment', 'dWAR', 'oWAR', 'replacement', 'noD_WAR']
    append_csv.writerow(csv_header)

    for row in res:
        append_csv.writerow(row)





if __name__ == "__main__":        



    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2018)
    parser.add_argument('--path',default='/Users/connordog/Desktop/')    
    args = parser.parse_args()
    
    process(args.year, args.path)

