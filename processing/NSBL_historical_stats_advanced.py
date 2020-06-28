from py_db import db

# Re-computes historical statistics for all NSBL players, and writes them to the db

db = db('NSBL')

def process():
    print "historical_stats_hitters_advanced"
    db.query("TRUNCATE TABLE `historical_stats_hitters_advanced`")
    db.query("TRUNCATE TABLE `historical_stats_pitchers_advanced`")

    hit_q = """
SELECT COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name) AS player_name
, GROUP_CONCAT(DISTINCT team_abb ORDER BY YEAR DESC SEPARATOR '/') AS teams
, MAX(YEAR) AS end_year
, MIN(YEAR) AS start_year
, COUNT(DISTINCT year) AS years
, SUM(w.pa) AS pa
, SUM(w.defense) AS defense
, SUM(w.position_adj) AS position_adj
, SUM(w.dWAR) AS dWAR
, SUM(o.park_wOBA*o.pa)/SUM(o.pa) AS park_wOBA
, SUM(o.OPS_plus*o.pa)/SUM(o.pa) AS OPS_plus
, SUM(o.wRC_plus*o.pa)/SUM(o.pa) AS wRC_plus
, SUM(o.rAA) as rAA
, SUM(w.oWAR) as oWAR
, SUM(w.replacement) as replacement
, SUM(w.WAR-w.defense/10) as "noD_WAR"
, SUM(w.WAR) as WAR
FROM processed_compWAR_offensive o
JOIN processed_WAR_hitters w USING (year, team_abb, player_name)
LEFT JOIN name_mapper nm ON (1
    AND o.player_name = nm.wrong_name
    AND (nm.start_year IS NULL OR nm.start_year <= o.year)
    AND (nm.end_year IS NULL OR nm.end_year >= o.year)
    AND (nm.position = '' OR nm.position = o.position)
    # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
    AND (nm.nsbl_team = '' OR nm.nsbl_team = o.team_abb)
)
GROUP BY COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name)
"""

    hit_vals = db.query(hit_q)
    hit_table = "historical_stats_hitters_advanced"
    hit_keys = ['player_name','teams','end_year','start_year','years','pa','defense','position_adj','dWAR','park_wOBA','OPS_plus','wRC_plus','rAA','oWAR','replacement','noD_WAR', 'WAR']

    hit_entries = []
    for row in hit_vals:
        entry = {}
        for k, v in zip(hit_keys, row):
            entry[k] = v
        hit_entries.append(entry)

    print '\thitters'
    db.insertRowDict(hit_entries, hit_table, replace=True, insertMany=True, rid=0)
    db.conn.commit()


    pitch_q = """
SELECT COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name) AS player_name
, GROUP_CONCAT(DISTINCT team_abb ORDER BY YEAR DESC SEPARATOR '/') AS teams
, MAX(YEAR) AS end_year
, MIN(YEAR) AS start_year
, COUNT(DISTINCT year) AS years
, SUM(ip) AS ip
, SUM(k_9*ip)/SUM(ip) AS k_9
, SUM(bb_9*ip)/SUM(ip) AS bb_9
, SUM(k_bb*ip)/SUM(ip) AS k_bb
, SUM(hr_9*ip)/SUM(ip) AS hr_9
, SUM(FIP*ip)/SUM(ip) AS FIP
, SUM(park_FIP*ip)/SUM(ip) AS park_FIP
, SUM(FIP_minus*ip)/SUM(ip) AS FIP_minus
, SUM(FIP_WAR) AS FIP_WAR
, SUM(ERA*ip)/SUM(ip) AS ERA
, SUM(park_ERA*ip)/SUM(ip) AS park_ERA
, SUM(ERA_minus*ip)/SUM(ip) AS ERA_minus
, SUM(ERA_WAR) AS ERA_WAR
FROM processed_WAR_pitchers o
LEFT JOIN name_mapper nm ON (1
    AND o.player_name = nm.wrong_name
    AND (nm.start_year IS NULL OR nm.start_year <= o.year)
    AND (nm.end_year IS NULL OR nm.end_year >= o.year)
    AND (nm.position = '' OR nm.position = o.position)
    # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
    AND (nm.nsbl_team = '' OR nm.nsbl_team = o.team_abb)
)
GROUP BY COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name)
"""
    pitch_vals = db.query(pitch_q)
    pitch_table = "historical_stats_pitchers_advanced"
    pitch_keys = ['player_name','teams','end_year','start_year','years','ip','k_9','bb_9','k_bb','hr_9','FIP','park_FIP','FIP_minus','FIP_WAR','ERA','park_ERA','ERA_minus','ERA_WAR']
    pitch_entries = []
    for row in pitch_vals:
        entry = {}
        for k, v in zip(pitch_keys, row):
            entry[k] = v
        pitch_entries.append(entry)

    print '\tpitchers'
    db.insertRowDict(pitch_entries, pitch_table, replace=True, insertMany=True, rid=0)
    db.conn.commit()


if __name__ == "__main__":     
    process()

