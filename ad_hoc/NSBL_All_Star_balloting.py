from py_db import db
import argparse
import csv


# Takes in a year range and team name, and writes out 6 csvs (primary hitting/pitching, advanced hitting/pitching, draft picks, free agents)


db = db('NSBL')


def process(year, path):
    for league in ('A', 'N'):
        if league == 'A':
            team_abbs = "IN ('ANA','LAA','HOU','OAK','TOR','CLE','CLV','SEA','BAL','BALT','TEX','TAM','TB','TBA','TBR','BOS','KC','KCR','DET','MIN','CHA','CHW','CWS','NYA','NYY')"
        else:
            team_abbs = "NOT IN ('ANA','LAA','HOU','OAK','TOR','CLE','CLV','SEA','BAL','BALT','TEX','TAM','TB','TBA','TBR','BOS','KC','KCR','DET','MIN','CHA','CHW','CWS','NYA','NYY','')"

        for position in ('dh','c','1b','2b','3b','ss','lf','cf','rf'):
            q = """SELECT *
FROM register_batting_primary
WHERE year = %s
AND position = '%s'
AND team_abb %s
AND ab >= 250
ORDER BY ab DESC
LIMIT 30;
"""

            qry = q % (year, position, team_abbs)

            as_qry = db.query(qry)

            allstar_title = path + league + '_' + position + '_All_Star_Ballot.csv'
            allstar_csv = open(allstar_title, 'wb')
            append_allstar_csv = csv.writer(allstar_csv)
            allstar_header = ['year','player_name','team_abb','position','age','avg','obp','slg','ab','h','2b','3b','hr','r','rbi','hbp','bb','k','sb','cs']
            append_allstar_csv.writerow(allstar_header)

            for row in as_qry:
                append_allstar_csv.writerow(row)




        sp_q = """SELECT *
FROM register_pitching_primary
WHERE year = %s
AND team_abb %s
AND ip >= 120
AND gs > (g*.40)
ORDER BY era ASC
LIMIT 75;
"""

        sp_qry = sp_q % (year, team_abbs)
        as_sp_qry = db.query(sp_qry)

        allstar_sp_title = path + league + '_' + 'sp' + '_All_Star_Ballot.csv'
        allstar_sp_csv = open(allstar_sp_title, 'wb')
        append_allstar_sp_csv = csv.writer(allstar_sp_csv)
        allstar_sp_header = ['year','player_name','team_abb','position','age','era','w','l','sv','g','gs','cg','sho','ip','h','r','er','bb','k','hr','gdp']
        append_allstar_sp_csv.writerow(allstar_sp_header)

        for row in as_sp_qry:
            append_allstar_sp_csv.writerow(row)



        rp_q = """SELECT *
FROM register_pitching_primary
WHERE year = %s
AND team_abb %s
AND ip >= 35
AND gs < (g*.40)
ORDER BY era ASC
LIMIT 50;
"""

        rp_qry = rp_q % (year, team_abbs)
        as_rp_qry = db.query(rp_qry)

        allstar_rp_title = path + league + '_' + 'rp' + '_All_Star_Ballot.csv'
        allstar_rp_csv = open(allstar_rp_title, 'wb')
        append_allstar_rp_csv = csv.writer(allstar_rp_csv)
        allstar_rp_header = ['year','player_name','team_abb','position','age','avg','obp','slg','ab','h','2b','3b','hr','r','rbi','hbp','bb','k','sb','cs']
        append_allstar_rp_csv.writerow(allstar_rp_header)

        for row in as_rp_qry:
            append_allstar_rp_csv.writerow(row)




if __name__ == "__main__":        



    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    parser.add_argument('--path',default='/Users/connordog/Desktop/')    
    args = parser.parse_args()
    
    process(args.year, args.path)

