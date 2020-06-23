from py_db import db

# Re-computes historical statistics for all NSBL players, and writes them to the db

db = db('NSBL')

def process():
    db.query("TRUNCATE TABLE `historical_stats_hitters_primary`")
    db.query("TRUNCATE TABLE `historical_stats_pitchers_primary`")

    hit_q = """
SELECT COALESCE(CONCAT(nm.right_fname, ' ', nm.right_lname), o.player_name) AS player_name
, GROUP_CONCAT(DISTINCT team_abb ORDER BY YEAR DESC SEPARATOR '/') AS teams
, MAX(YEAR) AS end_year
, MIN(YEAR) AS start_year
, COUNT(DISTINCT year) AS years
, SUM(pa) AS pa
, SUM(ab) AS ab
, SUM(h)/SUM(ab) as avg
, (SUM(h)+SUM(bb)+SUM(hbp))/SUM(pa) as obp
, (SUM(h)+SUM(2b)+SUM(3b)*2+SUM(hr)*3)/SUM(ab) as slg
, SUM(h) AS h
, SUM(2b) AS 2b
, SUM(3b) AS 3b
, SUM(hr) AS hr
, SUM(r) AS r
, SUM(rbi) AS rbi
, SUM(hbp) AS hbp
, SUM(bb) AS bb
, SUM(k) AS k
, SUM(sb) AS sb
, SUM(cs) AS cs
FROM register_batting_primary o
JOIN register_batting_secondary USING (year, player_name, team_abb, position, age)
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
    hit_table = "historical_stats_hitters_primary"
    hit_keys = ['player_name','teams','end_year','start_year','years','pa','ab','avg','obp','slg','h','2b','3b','hr','r','rbi','hbp','bb','k','sb','cs']

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
, 9*SUM(er)/SUM(ROUND(ip) + (10 * (ip - ROUND(ip)) / 3)) as era
, SUM(w) AS w
, SUM(l) AS l
, SUM(sv) AS sv
, SUM(g) AS g
, SUM(gs) AS gs
, SUM(cg) AS cg
, SUM(sho) AS sho
, SUM(ROUND(ip) + (10 * (ip - ROUND(ip)) / 3)) AS ip
, SUM(h) AS h
, SUM(r) AS r
, SUM(er) AS er
, SUM(bb) AS bb
, SUM(k) AS k
, SUM(hr) AS hr
, SUM(gdp) AS gdp
FROM register_pitching_primary o
JOIN register_pitching_secondary USING (year, player_name, team_abb, position, age)
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
    pitch_table = "historical_stats_pitchers_primary"
    pitch_keys = ['player_name','teams','end_year','start_year','years','era','w','l','sv','g','gs','cg','sho','ip','h','r','er','bb','k','hr','gdp']
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

