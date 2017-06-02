from py_db import db
import NSBL_helpers as helper

# Re-computes the advanced standings metrics and writes it to the db

db = db('NSBL')


def process():
    table = 'processed_team_standings_advanced'
    db.query("TRUNCATE TABLE `"+table+"`")

    entries = []
    teamWAR_qry = """SELECT
year,
team_abb,
dWAR,
oWAR,
(replacement/10) as repWAR,
FIP_WAR,
ERA_WAR
FROM processed_WAR_team
"""

    team_WAR_list = db.query(teamWAR_qry)

    for team in team_WAR_list:
        year, team_abb, dWAR, oWAR, repWAR, FIP_WAR, ERA_WAR = team

        mascot_name = helper.get_mascot_names(team_abb.upper())

        #a full season is ~17 replacement wins?
        repWAR = float(repWAR)

        pos_WAR = float(dWAR) + float(oWAR) + repWAR
        fWAR = pos_WAR + float(FIP_WAR)
        rWAR = pos_WAR + float(ERA_WAR)

        if team_abb == '':
            continue
        else:
            record_q = """SELECT
year,
team_name, 
w,
l,
rf,
ra
FROM team_standings
WHERE team_name LIKE '%%%s%%'
AND year = %s
"""
            record_qry = record_q % (mascot_name, year)

            record = db.query(record_qry)[0]

            year, team_name, w, l, rf, ra = record

            games = w+l

            # http://www.had2know.com/sports/pythagorean-expectation-win-percentage-baseball.html
            pythag_x = ((float(rf)+float(ra))/(float(w)+float(l)))**(float(0.285))
            pythag_win_pct = (float(rf)**pythag_x)/((float(rf)**pythag_x) + (float(ra)**pythag_x))
            pythag_wins = (w+l)*pythag_win_pct
            pythag_losses = games - (pythag_wins)

            rep_team_win_pct = 0.333
            rep_team_wins = rep_team_win_pct*games

            # f_wins = (pos_WAR/repWAR)*17.0 + float(FIP_WAR) + rep_team_wins
            # f_losses = games - (f_wins)
            # r_wins = (pos_WAR/repWAR)*17.0 + float(ERA_WAR) + rep_team_wins
            # r_losses = games - (r_wins)

            f_wins = fWAR + rep_team_wins
            f_losses = games - (f_wins)
            r_wins = rWAR + rep_team_wins
            r_losses = games - (r_wins)

            entry = {"year":year, "team_name":team_name, "repWAR":repWAR, "oWAR":oWAR, "dWAR":dWAR, "FIP_WAR":FIP_WAR, "ERA_WAR":ERA_WAR, "RF":rf, "RA":ra, "f_Wins":f_wins, "f_Losses":f_losses, "r_Wins":r_wins, "r_Losses":r_losses, "py_Wins":pythag_wins, "py_Losses":pythag_losses, "W":w, "L":l}

            entries.append(entry)

    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()

if __name__ == "__main__":     
    process()

