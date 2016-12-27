from py_db import db
import argparse
import csv
import NSBL_helpers as helper


# Takes in a year range and team name, and writes out 6 csvs (primary hitting/pitching, advanced hitting/pitching, draft picks, free agents)


db = db('NSBL')


def process(team_name, start_year, end_year, path):

    team_abbs, ta = helper.get_team_abbs(team_name)

    prim_hit_q = """
SELECT 
player_name,
COUNT(*) AS years,
SUM(pa) AS pa,
SUM(ab) AS ab,
SUM(h)/SUM(ab) as avg,
(SUM(h)+SUM(bb)+SUM(hbp))/SUM(pa) as obp,
(SUM(h)+SUM(2b)+SUM(3b)*2+SUM(hr)*3)/SUM(ab) as slg,
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
SUM(cs) AS cs
FROM register_batting_primary
JOIN register_batting_secondary USING (year, player_name, team_abb, age)
WHERE team_abb IN %s
AND year >= %s
AND year <=%s
GROUP BY player_name
ORDER BY pa DESC;
"""

    prim_hit_qry = prim_hit_q % (team_abbs, start_year, end_year)

    prim_hit = db.query(prim_hit_qry)

    csv_title = path + ta + '_hitter_primary.csv'
    prim_hit_csv = open(csv_title, 'wb')
    append_prim_hit_csv = csv.writer(prim_hit_csv)
    prim_hit_header = ['player_name', 'years', 'pa', 'ab', 'avg', 'obp', 'slg', 'h', '2b', '3b', 'hr', 'r', 'rbi', 'hbp', 'bb', 'k', 'sb', 'cs'] 
    append_prim_hit_csv.writerow(prim_hit_header)

    for row in prim_hit:
        append_prim_hit_csv.writerow(row)



    prim_pitch_q = """
SELECT 
player_name,
COUNT(*) AS years,
9*SUM(er)/SUM(ROUND(ip) + (10 * (ip - ROUND(ip)) / 3)) as era,
SUM(w) AS w,
SUM(l) AS l,
SUM(sv) AS sv,
SUM(g) AS g,
SUM(gs) AS gs,
SUM(cg) AS cg,
SUM(sho) AS sho,
SUM(ROUND(ip) + (10 * (ip - ROUND(ip)) / 3)) AS ip,
SUM(h) AS h,
SUM(r) AS r,
SUM(er) AS er,
SUM(bb) AS bb,
SUM(k) AS k,
SUM(hr) AS hr,
SUM(gdp) AS gdp
FROM register_pitching_primary
JOIN register_pitching_secondary USING (year, player_name, team_abb, age)
WHERE team_abb IN %s
AND year >= %s
AND year <=%s
GROUP BY player_name
ORDER BY ip DESC;
"""

    prim_pitch_qry = prim_pitch_q % (team_abbs, start_year, end_year)

    prim_pitch = db.query(prim_pitch_qry)

    csv_title = path + ta + '_pitcher_primary.csv'
    prim_pitch_csv = open(csv_title, 'wb')
    append_prim_pitch_csv = csv.writer(prim_pitch_csv)
    prim_pitch_header = ['player_name', 'years', 'era', 'w', 'l', 'sv', 'g', 'gs', 'cg', 'sho', 'ip', 'h', 'r', 'er', 'bb', 'k', 'hr', 'gdp'] 
    append_prim_pitch_csv.writerow(prim_pitch_header)

    for row in prim_pitch:
        append_prim_pitch_csv.writerow(row)



    adv_hit_q = """
SELECT 
player_name,
COUNT(*) AS years,
SUM(o.pa) AS pa,
SUM(d.defense) AS defense,
SUM(d.position_adj) AS position_adj,
SUM(d.dWAR) AS dWAR,
SUM(o.park_wOBA*o.pa)/SUM(o.pa) AS park_wOBA,
SUM(o.OPS_plus*o.pa)/SUM(o.pa) AS OPS_plus,
SUM(o.wRC_plus*o.pa)/SUM(o.pa) AS wRC_plus,
SUM(o.rAA) as rAA,
SUM(o.oWAR) as oWAR,
SUM(w.replacement) as replacement,
SUM(w.WAR) as WAR
FROM processed_compWAR_offensive o
JOIN processed_compWAR_defensive d USING (year, team_abb, player_name)
JOIN processed_WAR_hitters w USING (year, team_abb, player_name)
WHERE team_abb IN %s
AND year >= %s
AND year <=%s
GROUP BY player_name
ORDER BY WAR DESC;
"""

    adv_hit_qry = adv_hit_q % (team_abbs, start_year, end_year)

    adv_hit = db.query(adv_hit_qry)

    csv_title = path + ta + '_hitter_advanced.csv'
    adv_hit_csv = open(csv_title, 'wb')
    append_adv_hit_csv = csv.writer(adv_hit_csv)
    adv_hit_header = ['player_name', 'years', 'pa', 'defense', 'position_adj', 'dWAR', 'park_wOBA', 'OPS_plus', 'wRC_plus', 'rAA', 'oWAR', 'replacement', 'WAR'] 
    append_adv_hit_csv.writerow(adv_hit_header)

    for row in adv_hit:
        append_adv_hit_csv.writerow(row)



    adv_pitch_q = """
SELECT 
player_name,
COUNT(*) AS years,
SUM(ip) AS ip,
SUM(k_9*ip)/SUM(ip) AS k_9,
SUM(bb_9*ip)/SUM(ip) AS bb_9,
SUM(k_bb*ip)/SUM(ip) AS k_bb,
SUM(hr_9*ip)/SUM(ip) AS hr_9,
SUM(FIP*ip)/SUM(ip) AS FIP,
SUM(park_FIP*ip)/SUM(ip) AS park_FIP,
SUM(FIP_minus*ip)/SUM(ip) AS FIP_minus,
SUM(FIP_WAR) AS FIP_WAR,
SUM(ERA*ip)/SUM(ip) AS ERA,
SUM(park_ERA*ip)/SUM(ip) AS park_ERA,
SUM(ERA_minus*ip)/SUM(ip) AS ERA_minus,
SUM(ERA_WAR) AS ERA_WAR
FROM processed_WAR_pitchers p
WHERE team_abb IN %s
AND year >= %s
AND year <=%s
GROUP BY player_name
ORDER BY ERA_WAR DESC;
"""

    adv_pitch_qry = adv_pitch_q % (team_abbs, start_year, end_year)

    adv_pitch = db.query(adv_pitch_qry)

    csv_title = path + ta + '_pitcher_advanced.csv'
    adv_pitch_csv = open(csv_title, 'wb')
    append_adv_pitch_csv = csv.writer(adv_pitch_csv)
    adv_pitch_header = ['player_name', 'years', 'ip', 'k_9', 'bb_9', 'k_bb', 'hr_9', 'FIP', 'park_FIP', 'FIP_minus', 'FIP_WAR', 'ERA', 'park_ERA', 'ERA_minus', 'ERA_WAR'] 
    append_adv_pitch_csv.writerow(adv_pitch_header)

    for row in adv_pitch:
        append_adv_pitch_csv.writerow(row)



    draft_q = """
SELECT 
*
FROM historical_draft_picks hdp
WHERE team_abb IN %s
AND year >= %s
AND year <= %s
GROUP BY player_name
ORDER BY year, season, overall;
"""

    draft_qry = draft_q % (team_abbs, start_year, end_year)

    draft_picks = db.query(draft_qry)

    csv_title = path + ta + '_draft_picks.csv'
    draft_picks_csv = open(csv_title, 'wb')
    append_draft_picks_csv = csv.writer(draft_picks_csv)
    draft_picks_header = ['year','season','overall','round','pick','team_abb','player_name','position'] 
    append_draft_picks_csv.writerow(draft_picks_header)

    for row in draft_picks:
        append_draft_picks_csv.writerow(row)





    fa_q = """
SELECT 
*
FROM historical_free_agency hfa
WHERE signing_team IN %s
AND year >= %s
AND year <=%s
GROUP BY player_name
ORDER BY year, day;
"""

    fa_qry = fa_q % (team_abbs, start_year, end_year)

    fa_list = db.query(fa_qry)

    csv_title = path + ta + '_free_agency.csv'
    fa_csv = open(csv_title, 'wb')
    append_fa_csv = csv.writer(fa_csv)
    fa_header = ['year','day','signing_team','rights','player_name','contract_years','option','aav'] 
    append_fa_csv.writerow(fa_header)

    for row in fa_list:
        append_fa_csv.writerow(row)




if __name__ == "__main__":        



    parser = argparse.ArgumentParser()
    parser.add_argument('--team',default='white sox' )
    parser.add_argument('--start_year',default=2004 )
    parser.add_argument('--end_year',default=2017 )
    parser.add_argument('--path',default='/Users/connordog/Desktop/')    
    args = parser.parse_args()
    
    process(args.team, args.start_year, args.end_year, args.path)

