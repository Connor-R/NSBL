from py_db import db
import NSBL_helpers as helper

# Re-computes the team defense tables

db = db('NSBL')


def process():
    db.query("TRUNCATE TABLE `processed_team_defense`")
    for year in range(2006, 2018):
            print str(year) + "\tdefense"
            table = 'processed_team_defense'

            entries = process_defense(year)


            if entries != []: 
                db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
            db.conn.commit()


def process_defense(year):
    entries = []
    qry = """SELECT 
r.team_abb, SUM(defense), SUM(inn), SUM(dpa), SUM(p_adj), SUM(dWAR)
FROM register_batting_primary r
JOIN processed_compWAR_offensive o USING (player_name, team_abb, YEAR)
LEFT JOIN(
    SELECT
    player_name, team_abb, YEAR, SUM(defense) AS defense, 
    SUM(inn) AS inn,
    SUM(pa) AS dpa,
    SUM(position_adj) AS p_adj,
    SUM(dWAR) AS dWAR
    FROM processed_compWAR_defensive
    GROUP BY player_name, YEAR, team_abb
) d ON (r.player_name LIKE CONCAT(d.player_name,'%%') AND r.team_abb = d.team_abb AND r.year = d.year)
WHERE r.year = %s
GROUP BY r.team_abb"""

    query = qry % (year)
    res = db.query(query)

    for row in res:
        team_abb, defense, inn, dpa, pos_adj, dWAR = row

        entry = {}
        entry["year"] = year
        entry["team_abb"] = team_abb
        entry["pa"] = dpa
        entry["inn"] = inn
        entry["defense"] = defense
        entry["position_adj"] = pos_adj
        entry["dWAR"] = dWAR

        entries.append(entry)

    return entries



if __name__ == "__main__":     
    process()

