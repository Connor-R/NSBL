from py_db import db
import NSBL_helpers as helper


# Re-computes the team defense tables


db = db('NSBL')


def process():
    print "processed_team_defense"
    db.query("TRUNCATE TABLE `processed_team_defense`")

    yr_min, yr_max = db.query("SELECT MIN(year), MAX(year) FROM processed_league_averages_pitching")[0]

    for year in range(yr_min, yr_max+1):
            print str(year) + "\tdefense"
            table = 'processed_team_defense'

            entries = process_defense(year)


            if entries != []: 
                db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
            db.conn.commit()


def process_defense(year):
    entries = []
    qry = """SELECT 
    r.team_abb, SUM(defense), SUM(position_adj), SUM(dWAR)
    FROM register_batting_primary r
    JOIN processed_compWAR_offensive o USING (player_name, team_abb, YEAR)
    JOIN processed_WAR_hitters w USING (player_name, team_abb, YEAR)
    WHERE r.year = %s
    GROUP BY r.team_abb;"""

    query = qry % (year)
    res = db.query(query)

    for row in res:
        team_abb, defense, pos_adj, dWAR = row

        entry = {}
        entry["year"] = year
        entry["team_abb"] = team_abb
        entry["defense"] = defense
        entry["position_adj"] = pos_adj
        entry["dWAR"] = dWAR

        entries.append(entry)

    return entries


if __name__ == "__main__":     
    process()

