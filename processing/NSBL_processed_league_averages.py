from py_db import db

# Computes league averages over a range of years, and writes them to the db

db = db('NSBL')

print "processed_league_averages"

for y in range(2006,2021):
    year = str(y)
    print '\t', year
    hit_q = """
SELECT
"""+year+""",
SUM(pa) AS pa,
SUM(ab) AS ab,
SUM(h) AS h,
(SUM(h)-SUM(2b)-SUM(3b)-SUM(hr)) AS 1b,
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
((0.691*SUM(bb)+0.722*SUM(hbp)+0.884*(SUM(h)-SUM(2b)-SUM(3b)-SUM(hr))+1.257*SUM(2b)+1.593*SUM(3b)+2.058*SUM(hr)+0.2*SUM(sb)-0.398*SUM(cs))/(SUM(pa))) AS wOBA,
(SUM(h)-SUM(hr))/(SUM(ab)-SUM(k)-SUM(hr)) AS BABIP,
SUM(rc) AS rc,
SUM(r)*27/(SUM(ab)-SUM(h)) AS 'rc/27'
FROM register_batting_primary
JOIN register_batting_secondary USING (year, player_name, team_abb, position, age)
WHERE year = """+year+"""
"""

    hit_avgs = db.query(hit_q)[0]
    hit_table = "processed_league_averages_hitting"
    hit_keys = ['year','pa','ab','h','1b','2b','3b','hr','r','rbi','hbp','bb','k','sb','cs','wOBA','babip','rc','rc_27']
    db.insertRow(table=hit_table, keys=hit_keys, values=hit_avgs, replace=True)
    db.conn.commit()

    pitch_q = """
SELECT
"""+year+""",
9*SUM(er)/(SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3))) AS era,
SUM(w) AS w,
SUM(l) AS l,
SUM(sv) AS sv,
SUM(g) AS g,
SUM(gs) AS gs,
SUM(cg) AS cg,
SUM(sho) AS sho,
SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3)) AS ip,
SUM(h) AS h,
SUM(r) AS r,
SUM(er) AS er,
SUM(bb) AS bb,
SUM(k) AS k,
SUM(hr) AS hr,
SUM(gdp) AS gdp,
9*SUM(k)/(SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3))) AS k_9,
9*SUM(bb)/(SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3))) AS b_9,
SUM(k)/SUM(bb) AS k_bb,
9*SUM(hr)/(SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3))) AS hr_9,
9*SUM(er)/(SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3))) - ((13*SUM(hr))+(3*SUM(bb))-(2*SUM(k)))/(SUM(ROUND(IP) + (10 * (IP - ROUND(IP)) / 3))) AS fip_const
FROM register_pitching_primary
WHERE year = """+year+"""
"""
    pitch_avgs = db.query(pitch_q)[0]
    pitch_table = "processed_league_averages_pitching"
    pitch_keys = ['year','era','w','l','sv','g','gs','cg','sho','ip','h','r','er','bb','k','hr','gdp','k_9','bb_9','k_bb','hr_9','fip_const']
    db.insertRow(table=pitch_table, keys=pitch_keys, values=pitch_avgs, replace=True)
    db.conn.commit()

