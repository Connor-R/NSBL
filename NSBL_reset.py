from py_db import db

db = db('NSBL')

def initiate():
    queries = """SELECT @yr := MAX(year) AS yr_set FROM excel_rosters;
    SELECT @gp := MAX(gp) AS gp_set FROM excel_rosters WHERE year = @yr;

    DELETE
    FROM _trade_value
    WHERE year = @yr
    AND season_gp = @gp;

    DELETE
    FROM _trade_value_teams
    WHERE year = @yr
    AND season_gp = @gp;

    DELETE
    FROM excel_rosters
    WHERE year = @yr
    AND gp = @gp;

    DELETE
    FROM excel_team_summary
    WHERE year = @yr
    AND gp = @gp;

    DELETE
    FROM processed_compWAR_defensive
    WHERE year = @yr;

    DELETE
    FROM processed_compWAR_offensive
    WHERE year = @yr;

    DELETE team_standings
    FROM team_standings
    JOIN(
        SELECT year, team_name, MAX(games_played) AS games_played
        FROM team_standings
        WHERE year = @yr
        GROUP BY year, team_name
    ) a USING (year, team_name, games_played);

    DELETE update_log
    FROM update_log
    JOIN(
        SELECT MAX(update_date) AS update_date
        FROM update_log
        WHERE type = 'weekly'
        AND DATEDIFF(NOW(), update_date) < 6
    ) a USING (update_date);
    """

    q_list = queries.split(';')

    year = db.query(q_list[0])[0][0]
    gp = db.query(q_list[1])[0][0]

    print 'year:', year, ' and gp:', gp
    raw_input("continue?")

    for q in q_list[:-1]:
        print 'a\n', q
        db.query(q)
    db.conn.commit()


if __name__ == "__main__":     
    initiate()

