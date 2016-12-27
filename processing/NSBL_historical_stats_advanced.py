from py_db import db

# Re-computes historical statistics for all NSBL players, and writes them to the db

db = db('NSBL')

def process():
    db.query("TRUNCATE TABLE `historical_stats_hitters_advanced`")
    db.query("TRUNCATE TABLE `historical_stats_pitchers_advanced`")

    hit_q = """
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
FROM (
    SELECT *
    FROM (
        SELECT a.*, count(*) AS cnt
        FROM processed_compWAR_offensive a
        JOIN processed_compWAR_offensive b USING (year, player_name, age)
        GROUP BY year, player_name, age
    ) c
    WHERE (cnt = 1 OR team_abb = '')
) o
JOIN (
    SELECT 
    year,
    player_name,
    SUM(defense) as defense,
    SUM(position_adj) as position_adj,
    SUM(dWAR) as dWAR
    FROM processed_compWAR_defensive 
    GROUP BY year, player_name
) d USING (year, player_name)
JOIN processed_WAR_hitters w USING (year, team_abb, player_name)
GROUP BY player_name
"""

    hit_vals = db.query(hit_q)
    hit_table = "historical_stats_hitters_advanced"
    hit_keys = ['player_name','years','pa','defense','position_adj','dWAR','park_wOBA','OPS_plus','wRC_plus','rAA','oWAR','replacement','WAR']

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
FROM (
    SELECT *
    FROM (
        SELECT a.*, count(*) AS cnt
        FROM processed_WAR_pitchers a
        JOIN processed_WAR_pitchers b USING (year, player_name, position, age)
        GROUP BY year, player_name, position, age
    ) a
    WHERE (cnt = 1 OR team_abb = '')
) b
GROUP BY player_name
"""
    pitch_vals = db.query(pitch_q)
    pitch_table = "historical_stats_pitchers_advanced"
    pitch_keys = ['player_name','years','ip','k_9','bb_9','k_bb','hr_9','FIP','park_FIP','FIP_minus','FIP_WAR','ERA','park_ERA','ERA_minus','ERA_WAR']
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

