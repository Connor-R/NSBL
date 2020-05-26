from py_db import db
import NSBL_helpers as helper


# Re-computes the team hitting tables


db = db('NSBL')


def process():
    db.query("TRUNCATE TABLE `processed_team_hitting_basic`")
    db.query("TRUNCATE TABLE `processed_team_hitting_advanced`")
    for year in range(2006, 2021):
        for _type in ('basic', 'advanced'):
            print str(year) + "\thitting\t" + _type
            table = 'processed_team_hitting_%s' % (_type)

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
    r.team_abb, 
    SUM(pa), SUM(ab), SUM(h), SUM(2B), SUM(3b), SUM(Hr), SUM(r), SUM(rbi), SUM(hbp), SUM(bb), SUM(k), SUM(sb), SUM(cs)
    FROM register_batting_primary r
    JOIN processed_compWAR_offensive o USING (player_name, team_abb, YEAR)
    JOIN processed_WAR_hitters w USING (pa, player_name, team_abb, YEAR)
    WHERE r.year = %s
    GROUP BY r.team_abb;"""

    query = qry % (year)
    res = db.query(query)

    for row in res:
        team_abb, pa, ab, h, _2, _3, hr, r, rbi, hbp, bb, k, sb, cs = row

        entry = {}
        entry["year"] = year
        entry["team_abb"] = team_abb

        _1 = h - _2 - _3 - hr
        avg = float(h)/float(ab)
        obp = (float(h)+float(bb)+float(hbp))/float(pa)
        slg = (float(_1)+2*float(_2)+3*float(_3)+4*float(hr))/float(pa)

        entry["avg"] = avg
        entry["obp"] = obp
        entry["slg"] = slg
        entry["pa"] = pa
        entry["ab"] = ab
        entry["h"] = h
        entry["2b"] = _2
        entry["3b"] = _3
        entry["hr"] = hr
        entry["r"] = r
        entry["rbi"] = rbi 
        entry["hbp"] = hbp
        entry["bb"] = bb
        entry["k"] = k
        entry["sb"] = sb
        entry["cs"] = cs

        entries.append(entry)

    return entries


def process_advanced(year):
    entries = []
    qry = """SELECT 
    r.team_abb, SUM(pa), SUM(pf*pa)/SUM(pa), SUM(wOBA*pa)/SUM(pa), SUM(park_wOBA*pa)/SUM(pa), SUM(OPS*pa)/SUM(pa), SUM(OPS_plus*pa)/SUM(pa), SUM(babip*pa)/SUM(pa), SUM(wRC), SUM(wRC_27*pa)/SUM(pa), SUM(wRC_plus*pa)/SUM(pa), SUM(rAA), SUM(w.oWAR)
    FROM register_batting_primary r
    JOIN processed_compWAR_offensive o USING (player_name, team_abb, YEAR)
    JOIN processed_WAR_hitters w USING (pa, player_name, team_abb, YEAR)
    WHERE r.year = %s
    GROUP BY r.team_abb;"""

    query = qry % (year)
    res = db.query(query)

    for row in res:
        team_abb, pa, pf, woba, park_woba, ops, ops_plus, babip, wrc, wrc_27, wrc_plus, raa, owar = row

        entry = {}
        entry["year"] = year
        entry["team_abb"] = team_abb

        entry["pa"] = pa
        entry["pf"] = pf
        entry["wOBA"] = woba
        entry["park_wOBA"] = park_woba
        entry["OPS"] = ops
        entry["OPS_plus"] = ops_plus
        entry["babip"] = babip
        entry["wRC"] = wrc
        entry["wRC_27"] = wrc_27
        entry["wRC_plus"] = wrc_plus
        entry["rAA"] = raa
        entry["oWAR"] = owar

        entries.append(entry)

    return entries


if __name__ == "__main__":     
    process()

