import argparse
from time import time
import csv
import os

from py_db import db
db = db("NSBL")

def initiate(year):
    start_time = time()

    print "\nexporting to .csv"
    export_current_bracket(year)
    export_current_probabilities(year)

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nexport_playoff_brackets.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def export_current_bracket(year):
    print "\t current bracket"
    qry = """SELECT 
    year, series_id, team, opponent, 
    series_wins, series_losses, 
    CONCAT( ROUND(100*(team_seriesProb),1), "%%") AS win_series, 
    CONCAT( ROUND(100*(team_in3),1), "%%") AS in3, 
    CONCAT( ROUND(100*(team_in4),1), "%%") AS in4, 
    CONCAT( ROUND(100*(team_in5),1), "%%") AS in5, 
    CONCAT( ROUND(100*(team_in6),1), "%%") AS in6, 
    CONCAT( ROUND(100*(team_in7),1), "%%") AS in7
    FROM __in_playoff_bracket
    WHERE total_playoff_games_played = (SELECT MAX(total_playoff_games_played) FROM __in_playoff_bracket WHERE year = %s)
    AND year = %s
    AND strength_type = "projected";
    """

    query = qry % (year, year)

    res = db.query(query)

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"
    csv_title = path_base + "/NSBL_in_playoff_bracket.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Series ID", "Team Name", "Opponent Name",
    "Series Wins", "Series Losses",
    "Advance Probability", "Win in 3", "Win in 4", "Win in 5", "Win in 6", "Win in 7"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_current_probabilities(year):
    print "\t current probabilities"
    qry = """SELECT 
    year, team_name, 
    CONCAT( ROUND(100*(win_division),1), "%%") AS win_Div,
    CONCAT( ROUND(100*(IFNULL(GREATEST(1,win_wc),0)),1), "%%") AS make_Wild_Card,
    CONCAT( ROUND(100*(win_wc),1), "%%") AS win_Wild_Card,
    CONCAT( ROUND(100*(make_ds),1), "%%") AS make_LDS,
    CONCAT( ROUND(100*(make_cs),1), "%%") AS make_LCS,
    CONCAT( ROUND(100*(make_ws),1), "%%") AS make_WS,
    CONCAT( ROUND(100*(win_ws),1), "%%") AS win_WS 
    FROM __in_playoff_probabilities
    WHERE total_playoff_games_played = (SELECT MAX(total_playoff_games_played) FROM __in_playoff_probabilities WHERE year = %s)
    AND year = %s
    AND strength_type = "projected";
    """

    query = qry % (year, year)

    res = db.query(query)

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"
    csv_title = path_base + "/NSBL_in_playoff_probabilities.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team Name", "Win Div", "Make Wild Card", "Win Wild Card",
    "Make LDS", "Make LCS", "Make WS", "Win WS"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)


if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2018)

    args = parser.parse_args()
    
    initiate(args.year)

