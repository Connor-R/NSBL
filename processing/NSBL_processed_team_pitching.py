from py_db import db
import NSBL_helpers as helper

# Re-computes the team hitting tables

db = db('NSBL')


def process():
    db.query("TRUNCATE TABLE `processed_team_pitching_basic`")
    db.query("TRUNCATE TABLE `processed_team_pitching_advanced`")
    for year in range(2006, 2019):
        for _type in ('basic', 'advanced'):
            print str(year) + "\tpitching\t" + _type
            table = 'processed_team_pitching_%s' % (_type)

            if _type == 'basic':
                entries = process_basic(year)
            elif _type == 'advanced':
                entries = process_advanced(year)


            if entries != []: 
                db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
            db.conn.commit()


def process_basic(year):
    entries = []
    qry = """SELECT 
r.team_abb, SUM(w), SUM(l), SUM(sv), SUM(g), SUM(gs), SUM(cg), SUM(sho), ROUND(SUM(ROUND(r.ip) + (10 * (r.ip - ROUND(r.ip)) / 3)),1) AS ip, SUM(h), SUM(r), SUM(er), SUM(bb), SUM(k), SUM(hr), SUM(gdp)
FROM register_pitching_primary r
JOIN processed_WAR_pitchers p USING (player_name, team_abb, YEAR)
WHERE r.year = %s
GROUP BY r.team_abb"""

    query = qry % (year)
    res = db.query(query)

    for row in res:
        team_abb, w, l, sv, g, gs, cg, sho, ip, h, r, er, bb, k, hr, gdp = row

        entry = {}
        entry["year"] = year
        entry["team_abb"] = team_abb

        era = (float(er)/float(ip))*9

        entry["era"] = era
        entry["w"] = w
        entry["l"] = l
        entry["sv"] = sv
        entry["g"] = g
        entry["gs"] = gs
        entry["cg"] = cg
        entry["sho"] = sho
        entry["ip"] = ip
        entry["h"] = h
        entry["r"] = r
        entry["er"] = er
        entry["bb"] = bb
        entry["k"] = k
        entry["hr"] = hr
        entry["gdp"] = gdp

        entries.append(entry)

    return entries


def process_advanced(year):
    entries = []
    qry = """SELECT 
r.team_abb, ROUND(SUM(ROUND(r.ip) + (10 * (r.ip - ROUND(r.ip)) / 3)),1) AS ip, SUM(pf*p.ip)/SUM(p.ip), SUM(k_9*p.ip)/SUM(p.ip), SUM(bb_9*p.ip)/SUM(p.ip), SUM(hr_9*p.ip)/SUM(p.ip), SUM(FIP*p.ip)/SUM(p.ip), SUM(park_FIP*p.ip)/SUM(p.ip), SUM(FIP_minus*p.ip)/SUM(p.ip), SUM(FIP_WAR), SUM(p.ERA*p.ip)/SUM(p.ip), SUM(park_ERA*p.ip)/SUM(p.ip), SUM(ERA_minus*p.ip)/SUM(p.ip), SUM(ERA_WAR)
FROM register_pitching_primary r
JOIN processed_WAR_pitchers p USING (player_name, team_abb, YEAR)
WHERE r.year = %s
GROUP BY r.team_abb"""

    query = qry % (year)
    res = db.query(query)

    for row in res:
        team_abb, ip, pf, k9, bb9, hr9, fip, pfip, fip_min, fip_war, era, pera, era_min, era_war = row

        entry = {}
        entry["year"] = year
        entry["team_abb"] = team_abb

        kbb = float(k9)/float(bb9)

        entry["ip"] = ip
        entry["pf"] = pf
        entry["k_9"] = k9
        entry["bb_9"] = bb9
        entry["k_bb"] = kbb
        entry["hr_9"] = hr9
        entry["FIP"] = fip
        entry["park_FIP"] = pfip
        entry["FIP_minus"] = fip_min
        entry["FIP_WAR"] = fip_war
        entry["ERA"] = era
        entry["park_ERA"] = pera
        entry["ERA_minus"] = era_min
        entry["ERA_WAR"] = era_war

        entries.append(entry)

    return entries



if __name__ == "__main__":     
    process()

