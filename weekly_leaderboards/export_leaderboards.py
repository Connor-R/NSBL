import argparse
from time import time
import csv
import os

from py_db import db
db = db("NSBL")

def initiate(year):
    start_time = time()

    print "\nexporting to .csv"
    export_current_rosters(year)
    export_current_team_summary(year)
    export_historical_tables()
    export_historical_team_draft_table(year)
    export_historical_team_free_agency_table(year)

    export_standings(year)
    export_changes(year)

    export_milestones(year)

    export_hidden_teams(year)
    export_hidden_projections(year)
    export_hidden_FA_batters(year)
    export_hidden_FA_pitchers(year)

    export_hidden_value(year)

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "\n\nexport_leaderboards.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def export_current_rosters(year):

    print "\t current rosters"

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"

    t_name = 'current_rosters'
    table = 'excel_rosters'

    csv_title = path_base + "/NSBL_%s.csv" % (t_name)
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = []

    qry = """SELECT e.*
    FROM excel_rosters e
    JOIN (
        SELECT year
        , MAX(date) AS date
        FROM excel_rosters
        WHERE 1
            AND year = %s
    ) cur USING (year, date);"""

    query = qry % (year)

    res = db.query(query)

    col_names_qry = """SELECT `COLUMN_NAME` 
    FROM `INFORMATION_SCHEMA`.`COLUMNS` 
    WHERE `TABLE_SCHEMA`='NSBL' 
    AND `TABLE_NAME`='%s';"""

    col_names_query = col_names_qry % (table)

    col_names = db.query(col_names_query)

    for cn in col_names:
        csv_header.append(cn[0])

    append_csv.writerow(csv_header)

    for row in res:
        row = list(row)
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_current_team_summary(year):

    print "\t current team summary"

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"

    t_name = 'current_team_summary'
    table = 'excel_team_summary'

    csv_title = path_base + "/NSBL_%s.csv" % (t_name)
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = []

    qry = """SELECT e.*
    FROM excel_team_summary e
    JOIN (
        SELECT year
        , MAX(date) AS date
        FROM excel_team_summary
        WHERE 1
            AND year = %s
    ) cur USING (year, date);"""

    query = qry % (year)

    res = db.query(query)

    col_names_qry = """SELECT `COLUMN_NAME` 
    FROM `INFORMATION_SCHEMA`.`COLUMNS` 
    WHERE `TABLE_SCHEMA`='NSBL' 
    AND `TABLE_NAME`='%s';"""

    col_names_query = col_names_qry % (table)

    col_names = db.query(col_names_query)

    for cn in col_names:
        csv_header.append(cn[0])

    append_csv.writerow(csv_header)

    for row in res:
        row = list(row)
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_historical_tables():

    for t_name, table in {
            "historical_DraftPicks": "historical_draft_pick_performance", 
            "historical_FreeAgency": "historical_free_agent_performance",
            "hall_of_fame": "historical_hall_of_fame",
            "historical_StatsHitters": "historical_stats_hitters",
            "historical_StatsPitchers": "historical_stats_pitchers",
            "historical_rosters": "excel_rosters",
        }.items():

        print "\t " + str(t_name)

        path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"

        csv_title = path_base + "/NSBL_%s.csv" % (t_name)
        csv_file = open(csv_title, "wb")
        append_csv = csv.writer(csv_file)
        csv_header = []

        qry = """SELECT *
        FROM %s;"""

        query = qry % (table)

        res = db.query(query)

        col_names_qry = """SELECT `COLUMN_NAME` 
        FROM `INFORMATION_SCHEMA`.`COLUMNS` 
        WHERE `TABLE_SCHEMA`='NSBL' 
        AND `TABLE_NAME`='%s';"""

        col_names_query = col_names_qry % (table)

        col_names = db.query(col_names_query)

        for cn in col_names:
            csv_header.append(cn[0])

        append_csv.writerow(csv_header)

        for row in res:
            row = list(row)
            for i, val in enumerate(row):
                if type(val) in (str,):
                    row[i] = "".join([l if ord(l) < 128 else "" for l in val])
            append_csv.writerow(row)

def export_historical_team_draft_table(year):
    print "\t historical team draft table"

    query = """SELECT *
    FROM 
    (
        SELECT 
        'all' AS 'team_abb'
        UNION
        (SELECT
        team_abb
        FROM historical_draft_picks
        GROUP BY team_abb ASC)
    ) t"""

    for yr in range(2005, year+1):
        qry_extension = """
        LEFT JOIN (
            SELECT
            team_abb, COUNT(*) AS '%s'
            FROM historical_draft_picks
            WHERE year = %s
            GROUP BY team_abb
            UNION ALL
            SELECT
            'all' AS team_abb, COUNT(*) AS '%s'
            FROM historical_draft_picks
            WHERE player_name != '--skipped--'
            AND position != ''
            AND year = %s
        ) a%s USING (team_abb)"""
    

        query_extension = qry_extension % (yr, yr, yr, yr, yr)

        query += query_extension

    qry_append = """
    LEFT JOIN(
        SELECT
        team_abb, COUNT(*) AS 'all_picks'
        FROM historical_draft_picks
        GROUP BY team_abb
        UNION ALL
        SELECT
        'ALL' AS team_abb, COUNT(*) AS 'all_picks'
        FROM historical_draft_picks
        WHERE player_name != '--skipped--'
        AND position != ''
    ) _all USING (team_abb);"""

    query += qry_append

    res = db.query(query)

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"
    csv_title = path_base + "/NSBL_historical_TeamDraftTable.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team",]
    for yr in range(2005, year+1):
        csv_header.append(str(yr))
    csv_header.append("All_Picks")
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row)
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_historical_team_free_agency_table(year):
    print "\t historical team free agency table"

    query = """SELECT *
    FROM 
    (
        SELECT 
        'all' AS 'team_abb'
        UNION
        (SELECT
        signing_team AS 'team_abb'
        FROM historical_free_agency
        GROUP BY signing_team ASC)
    ) t"""

    for yr in range(2013, year+1):
        qry_extension = """
        LEFT JOIN(
            SELECT
            signing_team AS 'team_abb', 
            COUNT(*) AS '%s_players',
            SUM(aav*contract_years) AS '%s_money'
            FROM historical_free_agency
            WHERE YEAR = %s
            GROUP BY signing_team
            UNION ALL
            SELECT
            'ALL' AS team_abb, 
            COUNT(*) AS '%s_players',
            SUM(aav*contract_years) AS '%s_money'
            FROM historical_free_agency
            WHERE YEAR = %s
        ) a%s USING (team_abb)"""
    

        query_extension = qry_extension % (yr, yr, yr, yr, yr, yr, yr)

        query += query_extension

    qry_append = """
    LEFT JOIN(
        SELECT
        signing_team AS 'team_abb', 
        COUNT(*) AS 'all_players',
        SUM(aav*contract_years) AS 'all_money'
        FROM historical_free_agency
        GROUP BY signing_team
        UNION ALL
        SELECT
        'ALL' AS team_abb, 
        COUNT(*) AS 'all_players',
        SUM(aav*contract_years) AS 'all_money'
        FROM historical_free_agency
    ) _all USING (team_abb);"""

    query += qry_append

    res = db.query(query)

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"
    csv_title = path_base + "/NSBL_historical_TeamFreeAgencyTable.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team",]
    for yr in range(2013, year+1):
        csv_header.append(str(yr)+"_Players")
        csv_header.append(str(yr)+"_Money")
    csv_header.append("All_Players")
    csv_header.append("All_Money")
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row)
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_standings(year):
    print "\t standings"
    qry = """SELECT
    pp.year, pp.team_name, pp.games_played, division,
    # "|",
    current_W AS "cur_W", current_L AS "cur_L",
    FORMAT(IFNULL(py_wins,0),1) AS py_wins, FORMAT(IFNULL(py_losses,0),1) AS py_losses, 
    # "|",
    RIGHT(strength_pct,4) AS "ROS_win%%",
    FORMAT(mean_W,1) AS "mean_proj_W",
    FORMAT(mean_L,1) AS "mean_proj_L", 
    # "|",
    FORMAT(p_95,1) AS "95th_pctile",
    FORMAT(p_75,1) AS "75th_pctile",
    FORMAT(p_25,1) AS "25th_pctile",
    FORMAT(p_05,1) AS "5th_pctile",
    # "|",
    CONCAT( FORMAT(100*(win_division),1), "%%") AS win_Div,
    CONCAT( FORMAT(100*(wc_1+wc_2),1), "%%") AS make_Wild_Card,
    CONCAT( FORMAT(100*(make_ds),1), "%%") AS make_LDS,
    CONCAT( FORMAT(100*(make_cs),1), "%%") AS make_LCS,
    CONCAT( FORMAT(100*(make_ws),1), "%%") AS make_WS,
    CONCAT( FORMAT(100*(win_ws),1), "%%") AS win_WS 
    FROM __playoff_probabilities pp
    JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
    JOIN __team_strength USING (team_abb, team_name, year, games_played)
    LEFT JOIN processed_team_standings_advanced tsa ON (pp.year = tsa.year
        AND pp.team_name = tsa.team_name
        AND pp.games_played = tsa.games_played
    ) 
    WHERE 1
        AND pp.strength_type ="projected"
        AND pp.year = %s
    ORDER BY LEFT(division,2)="AL", RIGHT(division,4)="West", RIGHT(division,7)="Central", projected_W DESC;
    """

    query = qry % (year)

    res = db.query(query)

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"
    csv_title = path_base + "/NSBL_leaderboard_Standings.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team Name", "Games Played", "Division", 
    "W", "L", "Py Wins", "Py Losses", 
    "ROS Win%", "Mean Proj W", "Mean Proj L", 
    "95th Pctile", "75th Pctile", "25th Pctile", "5th Pctile",
    "Win Div", "Make Wild Card", "Make LDS", "Make LCS", "Make WS", "Win WS"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_changes(year):
    print "\t weekly changes"
    # db.query("SET @rowno=0;")
    qry = """DROP TABLE IF EXISTS __weekly_changes;
    CREATE TABLE __weekly_changes AS
    SELECT 
    @rowno:=@rowno+1 AS "rank",
    year, team_name, division, games_played, week_W, week_L,
    # "|",
    IF(games_won_change<0,games_won_change,CONCAT("+",games_won_change)) AS games_won_change,
    # "|",
    win_Divisional_change,
    make_Wild_Card_change,
    make_LDS_change,
    make_LCS_change,
    make_World_Series_change,
    win_World_Series_change,
    weekly_impv,
    team_abb
    FROM(
        SELECT team_name, division, year AS "year", w0.games_played, 
        w0.current_w-w1.current_w AS week_W, w0.current_l-w1.current_l AS week_L,
        FORMAT(w0.mean_W-w1.mean_W,1) AS "games_won_change",
        CONCAT( FORMAT(1*FORMAT(w0.win_division-w1.win_division,3),1), "%%") AS "win_Divisional_change",
        CONCAT( FORMAT(1*FORMAT(w0.make_Wild_Card-w1.make_Wild_Card,3),1), "%%") AS "make_Wild_Card_change",
        CONCAT( FORMAT(1*FORMAT(w0.make_LDS-w1.make_LDS,3),1), "%%") AS "make_LDS_change",
        CONCAT( FORMAT(1*FORMAT(w0.make_LCS-w1.make_LCS,3),1), "%%") AS "make_LCS_change",
        CONCAT( FORMAT(1*FORMAT(w0.make_World_Series-w1.make_World_Series,3),1), "%%") AS "make_World_Series_change",
        CONCAT( FORMAT(1*FORMAT(w0.win_World_Series-w1.win_World_Series,3),1), "%%") AS "win_World_Series_change",
        ROUND( (w0.mean_W-w1.mean_W) + (w0.win_World_Series-w1.win_World_Series), 3) AS "weekly_impv",
        t.team_abb,
        @rowno:=0 as set_row
        FROM(
            SELECT 
            pp.team_name, division, year AS "year", games_played, mean_W, ts.current_w, ts.current_l,
            CONCAT( FORMAT(100*FORMAT(win_division,3),1), "%%") AS win_Division,
            CONCAT( FORMAT(100*FORMAT(wc_1+wc_2,3),1), "%%") AS make_Wild_Card,
            CONCAT( FORMAT(100*FORMAT(make_ds,3),1), "%%") AS make_LDS,
            CONCAT( FORMAT(100*FORMAT(make_cs,3),1), "%%") AS make_LCS,
            CONCAT( FORMAT(100*FORMAT(make_ws,3),1), "%%") AS make_World_Series,
            CONCAT( FORMAT(100*FORMAT(win_ws,3),1), "%%") AS win_World_Series 
            FROM __playoff_probabilities pp
            JOIN (SELECT team_abb, MAX(year) AS "year", MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
            JOIN __team_strength ts USING (team_abb, year, games_played)
            WHERE strength_type="projected"
            ORDER BY LEFT(division,2)="AL", RIGHT(division,4)="West", RIGHT(division,7)="Central", win_division DESC, wc_1+wc_2 DESC
        ) w0
        JOIN(
            SELECT 
            pp.team_name, division, year AS "year", games_played, mean_W, ts.current_w, ts.current_l,
            CONCAT( FORMAT(100*FORMAT(win_division,3),1), "%%") AS win_Division,
            CONCAT( FORMAT(100*FORMAT(wc_1+wc_2,3),1), "%%") AS make_Wild_Card,
            CONCAT( FORMAT(100*FORMAT(make_ds,3),1), "%%") AS make_LDS,
            CONCAT( FORMAT(100*FORMAT(make_cs,3),1), "%%") AS make_LCS,
            CONCAT( FORMAT(100*FORMAT(make_ws,3),1), "%%") AS make_World_Series,
            CONCAT( FORMAT(100*FORMAT(win_ws,3),1), "%%") AS win_World_Series
            FROM __playoff_probabilities pp
            JOIN (SELECT * FROM (SELECT team_abb, MAX(year) AS year, (games_played) AS games_played, @rowNumber:=@rowNumber+1 AS rn FROM __playoff_probabilities JOIN (SELECT @rowNumber:= 0) r WHERE year = %s GROUP BY team_abb, year, games_played) t WHERE rn %% (SELECT FORMAT(COUNT(*)/60,0) FROM __playoff_probabilities WHERE year = %s) = (SELECT FORMAT(COUNT(*)/60,0) FROM __playoff_probabilities WHERE year = %s)-1 ) t2 USING (team_abb, year, games_played)
            JOIN __team_strength ts USING (team_abb, year, games_played)
            WHERE strength_type="projected"
            ORDER BY LEFT(division,2)="AL", RIGHT(division,4)="West", RIGHT(division,7)="Central", win_division DESC, wc_1+wc_2 DESC
        ) w1 USING (team_name, division, year)
        JOIN teams t USING (team_name, year, division)
        ORDER BY weekly_impv desc
    )a;""" % (year, year, year)

    for q in qry.split(";"):
        if q.strip() != "":
            # print(q)
            db.query(q)
            db.conn.commit()

    query = "select * from __weekly_changes;"
    res = db.query(query)

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"
    csv_title = path_base + "/NSBL_leaderboard_Changes.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team Name", "Division", "Games", "week_W", "week_L",
    "Projected Wins Change", "Win Division Change", "Make Wild Card Change",
    "Make LDS Change", "Make LCS Change", "Make World Series Change", "Win World Series Change"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[2:-2])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)    

def export_milestones(year):
    print "\t milestones"
    qry = """drop table if exists milestones;
        create table milestones as
        select b.trophy_name
        , concat(round(b.score,0), if(b.score_type = 'record', ' *NSBL record*', '')) as milestone
        , 'career' as milestone_type
        , t.player_name
        , coalesce(h.team, p.team) as team
        , round(t.score,0) as player_value
        , if(b.score = t.score, '***', concat(round(b.score-t.score,0), ' to '
            , if(b.score_type = 'record', concat('NSBL record (', round(b.score), ' - ', plyrs, ')'), concat('milestone (', round(b.score), ')'))
        )
        ) as details
        from(
            select a.trophy_name
            , score
            , 'record' as score_type
            , group_concat(t.player_name separator '/') as plyrs
            from(
                select trophy_name
                , trophy_type
                , score
                from trophies
                where 1
                    and trophy_type = 'player_alltimecareer'
                    and rank = 1
                    and trophy_name not in ('hitters_bb%%'
                        , 'hitters_k%%', 'hitters_ops+', 'hitters_obp', 'hitters_raa', 'hitters_avg', 'hitters_slg', 'hitters_wrc+', 'hitters_opbs+', 'hitters_nodrs_war', 'hitters_war'
                        , 'pitchers_bb/9', 'pitchers_era', 'pitchers_era_minus', 'pitchers_fip', 'pitchers_fip_minus', 'pitchers_hr/9', 'pitchers_k/9', 'pitchers_k/bb', 'pitchers_era_war', 'pitchers_fip_war'
                    )
                group by trophy_name
            ) a 
            join trophies t using (trophy_name, score, trophy_type)
            group by trophy_name
            union all
            select
            'HITTERS_2b'
            , 500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_2b'
            , 400
            , 'milestone'
            , null
            union all
            select
            'HITTERS_2b'
            , 300
            , 'milestone'
            , null
            union all
            select
            'HITTERS_3b'
            , 100
            , 'milestone'
            , null
            union all
            select
            'HITTERS_3b'
            , 75
            , 'milestone'
            , null
            union all
            select
            'HITTERS_3b'
            , 50
            , 'milestone'
            , null
            union all
            select
            'HITTERS_bb'
            , 2000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_bb'
            , 1500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_bb'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_h'
            , 2000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_h'
            , 1500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_h'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_hr'
            , 450
            , 'milestone'
            , null
            union all
            select
            'HITTERS_hr'
            , 400
            , 'milestone'
            , null
            union all
            select
            'HITTERS_hr'
            , 300
            , 'milestone'
            , null
            union all
            select
            'HITTERS_k'
            , 2000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_k'
            , 1500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_k'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_r'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_r'
            , 750
            , 'milestone'
            , null
            union all
            select
            'HITTERS_r'
            , 500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_rbi'
            , 1250
            , 'milestone'
            , null
            union all
            select
            'HITTERS_rbi'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'HITTERS_rbi'
            , 750
            , 'milestone'
            , null
            union all
            select
            'HITTERS_rbi'
            , 500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_sb'
            , 500
            , 'milestone'
            , null
            union all
            select
            'HITTERS_sb'
            , 250
            , 'milestone'
            , null
            union all
            select
            'HITTERS_sb'
            , 100
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_bb'
            , 750
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_bb'
            , 500
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_cg'
            , 50
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_cg'
            , 25
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_g'
            , 750
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_g'
            , 500
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_ip'
            , 2500
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_ip'
            , 2000
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_ip'
            , 1500
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_ip'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_k'
            , 2500
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_k'
            , 2000
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_k'
            , 1500
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_k'
            , 1000
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_sv'
            , 200
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_sv'
            , 150
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_sv'
            , 100
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_w'
            , 200
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_w'
            , 150
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_w'
            , 100
            , 'milestone'
            , null
        ) b
        left join trophies t on (b.trophy_name = t.trophy_name
            and t.score >= least(b.score*0.95, b.score-5)
            and t.score <= b.score
            and t.trophy_type = 'player_alltimecareer'
        )
        left join historical_stats_hitters h on (%s = h.year_span and t.player_name = h.player_name and h.group_type = 'full_season')
        left join historical_stats_pitchers p on (%s = p.year_span and t.player_name = p.player_name and p.group_type = 'full_season')
        where 1
            and (h.player_name is not null or p.player_name is not null)
        group by b.trophy_name, b.score_type, h.player_name, p.player_name
        union all
        select b.trophy_name
        , concat(round(b.score,0), if(b.score_type = 'record', ' *NSBL record*', '')) as milestone
        , 'season' as milestone_type
        , t.player_name
        , coalesce(h.team, p.team) as team
        , concat(round(t.score,0), ', on pace for ', round(t.score/(plap.gs/(30*162)),0)) as player_value
        , concat(case
            when b.score < round(t.score/(plap.gs/(30*162))) then concat(round(abs(b.score-(t.score/(plap.gs/(30*162)))),0), ' over ')
            when b.score = round(t.score/(plap.gs/(30*162))) then 'On '
            else concat(round(abs(b.score-(t.score/(plap.gs/(30*162)))),0), ' off ')
        end
        , if(score_type='milestone', concat('pace for ', round(b.score,0)), concat('record pace (', round(b.score), ' - ', plyrs, ')'))
        ) as details
        from(
            select a.trophy_name
            , score
            , 'record' as score_type
            , group_concat(concat(t.player_name, '(', t.year, ')') separator '/') as plyrs
            from(
                select trophy_name
                , trophy_type 
                , score
                from trophies
                where 1
                    and trophy_type = 'player_AllTimeSingleSeason'
                    and rank = 1
                    and trophy_name not in ('hitters_bb%%'
                        , 'hitters_k%%', 'hitters_ops+', 'hitters_obp', 'hitters_raa', 'hitters_avg', 'hitters_slg', 'hitters_wrc+', 'hitters_opbs+', 'hitters_nodrs_war', 'hitters_war'
                        , 'pitchers_bb/9', 'pitchers_era', 'pitchers_era_minus', 'pitchers_fip', 'pitchers_fip_minus', 'pitchers_hr/9', 'pitchers_k/9', 'pitchers_k/bb', 'pitchers_era_war', 'pitchers_fip_war'
                    )
                group by trophy_name
            ) a 
            join trophies t using (trophy_name, score, trophy_type)
            group by trophy_name
            union all
            select
            'HITTERS_2b'
            , 50
            , 'milestone'
            , null
            union all
            select
            'HITTERS_3b'
            , 15
            , 'milestone'
            , null
            union all
            select
            'HITTERS_bb'
            , 100
            , 'milestone'
            , null
            union all
            select
            'HITTERS_h'
            , 200
            , 'milestone'
            , null
            union all
            select
            'HITTERS_hr'
            , 50
            , 'milestone'
            , null
            union all
            select
            'HITTERS_k'
            , 200
            , 'milestone'
            , null
            union all
            select
            'HITTERS_r'
            , 100
            , 'milestone'
            , null
            union all
            select
            'HITTERS_rbi'
            , 100
            , 'milestone'
            , null
            union all
            select
            'HITTERS_sb'
            , 50
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_bb'
            , 100
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_cg'
            , 10
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_g'
            , 80
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_ip'
            , 200
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_k'
            , 200
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_sv'
            , 30
            , 'milestone'
            , null
            union all
            select
            'PITCHERS_w'
            , 20
            , 'milestone'
            , null
        ) b
        join processed_league_averages_pitching plap on (plap.year = %s)
        left join trophies t on (b.trophy_name = t.trophy_name
            and t.score/(plap.gs/(30*162)) >= least(b.score*.95, b.score-5)
            and t.trophy_type = 'player_AllTimeSingleSeason'
            and t.year = plap.year
        )
        left join historical_stats_hitters h on (t.year = h.year_span and t.player_name = h.player_name and h.group_type = 'full_season')
        left join historical_stats_pitchers p on (t.year = p.year_span and t.player_name = p.player_name and p.group_type = 'full_season')
        where 1
            and (h.player_name is not null or p.player_name is not null)
        group by b.trophy_name, b.score_type, h.player_name, p.player_name
    ;""" % (year, year, year)

    for q in qry.split(";"):
        if q.strip() != "":
            # print(q)
            db.query(q)
            db.conn.commit()

    path_base = "/Users/connordog/Dropbox/Desktop_Files/Work_Things/connor-r.github.io/csvs"

    t_name = 'milestones'
    table = 'milestones'

    csv_title = path_base + "/NSBL_%s.csv" % (t_name)
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = []

    query = "select * from milestones"

    res = db.query(query)

    col_names_qry = """SELECT `COLUMN_NAME` 
    FROM `INFORMATION_SCHEMA`.`COLUMNS` 
    WHERE `TABLE_SCHEMA`='NSBL' 
    AND `TABLE_NAME`='%s';"""

    col_names_query = col_names_qry % (table)

    col_names = db.query(col_names_query)

    for cn in col_names:
        csv_header.append(cn[0])

    append_csv.writerow(csv_header)

    for row in res:
        row = list(row)
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)  

def export_hidden_batters(year):
    print "\t hidden batters"
    qry = """SELECT a.year
    , COALESCE(CONCAT(nm2.right_fname, ' ', nm2.right_lname), a.player_name) AS player_name
    , a.age
    , MAX(cre.current_team) AS current_team
    , MAX(cre.salary) AS salary
    , MAX(cre.contract_year) AS contract_year
    , MAX(cre.expires) AS expires
    , MAX(cre.NTC) AS NTC
    , a.teams
    , a.positions
    , defensive_innings
    , a.pa
    , a.ab
    , a.avg
    , a.obp
    , a.slg
    , a.h
    , a.1b
    , a.2b
    , a.3b
    , a.hr
    , a.r
    , a.rbi
    , a.bb
    , a.k
    , a.sb
    , a.cs
    , a.bb_pct
    , a.k_pct
    , a.iso
    , a.babip
    , a.OPS_plus
    , a.wRC_plus
    , a.RAA
    , a.wRC_27
    , a.DRS
    , a.position_adj_runs
    , a.dWAR
    , a.oWAR
    , a.replacement_runs
    , a.noD_WAR
    , a.WAR
    FROM(
        SELECT 
        year
        , player_name
        , age
        , GROUP_CONCAT(team_abb ORDER BY pa DESC SEPARATOR '/') AS teams
        , IFNULL(positions, 'dh') AS positions
        , defensive_innings
        , SUM(w.pa) AS pa
        , SUM(r.ab) AS ab
        , IF(SUM(avg*pa)/SUM(pa)<1, RIGHT(FORMAT(SUM(avg*pa)/SUM(pa),3), 4), FORMAT(SUM(avg*pa)/SUM(pa),3)) AS avg
        , IF(SUM(obp*pa)/SUM(pa)<1, RIGHT(FORMAT(SUM(obp*pa)/SUM(pa),3), 4), FORMAT(SUM(obp*pa)/SUM(pa),3)) AS obp
        , IF(SUM(slg*pa)/SUM(pa)<1, RIGHT(FORMAT(SUM(slg*pa)/SUM(pa),3), 4), FORMAT(SUM(slg*pa)/SUM(pa),3)) AS slg
        , SUM(r.h) AS h
        , SUM(r.h-r.2b-r.3b-r.hr) AS 1b
        , SUM(r.2b) AS 2b
        , SUM(r.3b) AS 3b
        , SUM(r.hr) AS hr
        , SUM(r.r) AS r
        , SUM(r.rbi) AS rbi
        , SUM(r.bb) AS bb
        , SUM(r.k) AS k
        , SUM(r.sb) AS sb
        , SUM(r.cs) AS cs
        , FORMAT(SUM((100*bb/w.pa)*(pa))/SUM((pa)),1) AS 'bb_pct'
        , FORMAT(SUM((100*k/ab)*(pa))/SUM((pa)),1) AS 'k_pct'
        , IF(SUM((slg-AVG)*pa)/SUM(pa)<1, RIGHT(FORMAT(SUM((slg-AVG)*pa)/SUM(pa),3), 4), FORMAT(SUM((slg-AVG)*pa)/SUM(pa),3)) AS 'iso'
        , IF(SUM(babip*pa)/SUM(pa)<1, RIGHT(FORMAT(SUM(babip*pa)/SUM(pa),3), 4), FORMAT(SUM(babip*pa)/SUM(pa),3)) AS babip
        , FORMAT(SUM(OPS_plus*pa)/SUM(pa),1) AS OPS_plus
        , FORMAT(SUM(wRC_plus*pa)/SUM(pa),1) AS wRC_plus
        , FORMAT(SUM(RAA),1) AS RAA
        , FORMAT(SUM(wRC_27*pa)/SUM(pa),1) AS wRC_27
        , FORMAT(SUM(defense),1) AS DRS
        , FORMAT(position_adj,1) AS position_adj_runs
        , FORMAT(SUM(position_adj)/10,1) AS dWAR
        , FORMAT(SUM(oWAR),1) AS oWAR
        , FORMAT(SUM(replacement),1) AS replacement_runs
        , FORMAT(SUM(WAR-defense/10),1) AS noD_WAR
        , FORMAT(SUM(WAR),1) AS WAR
        FROM processed_WAR_hitters w
        JOIN processed_compWAR_offensive USING (year, player_name, team_abb, age, position, pa, oWAR)
        JOIN register_batting_primary r USING (year, player_name, team_abb, age, position)
        LEFT JOIN(
            SELECT 
            year
            , player_name
            , team_abb
            , SUM(inn) AS defensive_innings
            , IF(
                (162*o.pa/600)/(SUM(inn)/9)<1.2,
                GROUP_CONCAT(d.position ORDER BY inn DESC SEPARATOR '/'),
                IF((162*o.pa/600)/(SUM(inn)/9)>2.0
                    , CONCAT('dh/', GROUP_CONCAT(d.position ORDER BY inn DESC SEPARATOR '/'))
                    , CONCAT(GROUP_CONCAT(d.position ORDER BY inn DESC SEPARATOR '/'), '/dh')
                )
            ) AS positions
            FROM processed_compWAR_defensive d
            JOIN processed_compWAR_offensive o USING (year, team_abb, player_name)
            WHERE 1
                AND year = %s
            GROUP BY player_name, year, team_abb
        ) d USING (year, player_name, team_abb)
        WHERE 1
            AND year = %s
            AND team_abb != ''
        GROUP BY player_name, year
    ) a
    LEFT JOIN name_mapper nm ON (1
        AND a.player_name = nm.wrong_name
        AND (nm.start_year IS NULL OR nm.start_year <= a.year)
        AND (nm.end_year IS NULL OR nm.end_year >= a.year)
        # AND (nm.position = '' OR nm.position = a.position)
        # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
        # AND (nm.nsbl_team = '' OR nm.nsbl_team = a.team_abb)
    )
    LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
        AND nm.right_lname = nm2.right_lname
        AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
        AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
        AND (nm.position = '' OR nm.position = nm2.position)
        AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
    )
    LEFT JOIN(
        SELECT player_name
        , team_abb as current_team
        , salary
        , contract_year as contract_year
        , expires
        , NTC
        , position
        FROM excel_rosters
        JOIN (
            SELECT year
            , MAX(date) AS date
            FROM excel_rosters
            WHERE 1
                AND year = %s
        ) cur USING (year, date)
    ) cre ON (1
        AND (cre.position != 'p'
            OR cre.player_name in ('Shohei Ohtani')
        )
        AND IFNULL(nm2.wrong_name, a.player_name) = cre.player_name
    )
    GROUP BY year, COALESCE(CONCAT(nm2.right_fname, ' ', nm2.right_lname), a.player_name)
    ;"""

    query = qry % (year, year, year)

    res = db.query(query)

    csv_title = os.getcwd() + "/HIDDEN_Batters.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = [ "Player Name", "Age", 
    "Current Team", "Salary", "Contract Year", "Contract Expires", "NTC",
    "Teams", "Positions", "Innings",
    "PA", "AB", 
    "AVG", "OBP", "SLG",
    "H", "1B", "2B", "3B", "HR", 
    "R", "RBI", 
    "BB", "K", "SB", "CS",
    "BB%", "K%", "ISO",
    "BABIP", "OPS+", "wRC+",
    "RAA", "wRC/27",
    "DRS", "PosAdj",
    "dWAR", "oWAR", "Rep",
    "noD WAR",
    "Total WAR"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)  

def export_hidden_teams(year):
    print "\t hidden teams"
    qry = """SELECT 
    year, team_name, games_played, 
    FORMAT(repWAR,1) AS repWAR, FORMAT(oWAR,1) AS oWAR, FORMAT(dWAR,1) AS dWAR, 
    FORMAT(FIP_WAR,1) AS FIP_WAR, FORMAT(ERA_WAR,1) AS ERA_WAR, 
    RF, RA, 
    FORMAT(f_Wins,1) AS f_Wins, FORMAT(f_Losses,1) AS f_Losses, 
    FORMAT(r_Wins,1) AS r_Wins, FORMAT(r_Losses,1) AS r_Losses, 
    FORMAT(py_Wins,1) AS py_Wins, FORMAT(py_Losses,1),
    W, L
    FROM processed_team_standings_advanced
    JOIN (
        SELECT year, team_name, MAX(games_played) AS 'games_played' 
        FROM processed_team_standings_advanced 
        GROUP BY year, team_name
    ) a USING (year, team_name, games_played)
    WHERE year=%s;"""

    query = qry % (year)

    res = db.query(query)

    csv_title = os.getcwd() + "/HIDDEN_Teams.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team Name", "Games",
    "Replacement WAR", "oWAR", "dWAR",
    "FIP_WAR", "ERA_WAR",
    "Runs_For", "Runs_Against",
    "f Wins", "f Losses", 
    "r Wins", "r Losses",
    "py Wins", "py Losses",
    "W", "L"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_hidden_projections(year):
    print "\t hidden projections"
    qry = """SELECT
    year, team_name,  games_played,
    FORMAT(roster_strength,1) AS roster_strength,
    FORMAT(roster_W,1) AS roster_W,
    FORMAT(roster_L,1) AS roster_L,
    RIGHT(roster_pct,4) as roster_pct,
    current_W, current_L, RIGHT(current_pct,4) AS current_pct,
    FORMAT(ros_W,1) AS ros_W,
    FORMAT(ros_L,1) AS ros_L,
    RIGHT(ros_pct,4) as ros_pct,
    FORMAT(projected_W,1) AS projected_W,
    FORMAT(projected_L,1) AS projected_L,
    RIGHT(projected_pct,4) as projected_pct
    FROM __team_strength
    JOIN (SELECT team_name, MAX(year) AS year, MAX(games_played) AS games_played FROM __team_strength GROUP BY team_name, year) t2 USING (team_name, year, games_played)
    WHERE year = %s
    ORDER BY projected_pct DESC;"""

    query = qry % (year)

    res = db.query(query)

    csv_title = os.getcwd() + "/HIDDEN_Projections.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Team_Name", "Games",
    "Roster_Strength", "Roster_W", "Roster_L", "Roster%",
    "Current_W", "Current_L", "Current%",
    "ROS_W", "ROS_L", "ROS%",
    "Projected_W", "Projected_L", "Projected%"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_hidden_FA_batters(year):
    print "\t hidden FA batters"
    qry = """SELECT a.year
    , COALESCE(CONCAT(nm2.right_fname, ' ', nm2.right_lname), a.player_name) AS player_name
    , a.team_abb
    , IFNULL(MAX(t.team_name), "FREE AGENT") AS team
    , MAX(cre.salary) AS salary
    , MAX(cre.contract_year) AS contract_year
    , MAX(cre.expires) AS expires
    , MAX(cre.NTC) AS NTC
    , a.age
    , a.position
    , a.bats
    , a.pf
    , a.position_adj
    , a.rn
    , a.er
    , a.arm
    , a.pb
    , a.DRS
    , a.dWAR
    , a.vsL_wRC_plus
    , a.vsR_wRC_plus
    , a.babip
    , a.ops_plus
    , a.wrc_plus
    , a.vsL_oWAR
    , a.vsR_oWAR
    , a.oWAR
    , a.vsL_WAR
    , a.vsR_WAR
    , a.WAR
    FROM(
        SELECT year
        , z.player_name
        , z.team_abb
        , t.team_abb as nsbl_roster
        , z.age
        , z.position
        , z.bats
        , z.pf
        , z.position_adj
        , z.rn
        , z.er
        , z.arm
        , z.pb
        , FORMAT(z.DRS,1) AS DRS
        , FORMAT(z.dWAR,2) AS dWAR
        , FORMAT(z.vsL_wRC_plus,1) AS vsL_wRC_plus
        , FORMAT(z.vsR_wRC_plus,1) AS vsR_wRC_plus
        , RIGHT(FORMAT(z2.babip,3),4) AS babip
        , FORMAT(z2.ops_plus,1) AS ops_plus
        , FORMAT(z.wrc_plus,1) AS wrc_plus
        , FORMAT(z.vsL_oWAR,2) AS vsL_oWAR
        , FORMAT(z.vsR_oWAR,2) AS vsR_oWAR
        , FORMAT(z.oWAR,2) AS oWAR
        , FORMAT(z.vsL_WAR,2) AS vsL_WAR
        , FORMAT(z.vsR_WAR,2) AS vsR_WAR
        , FORMAT(z.WAR,2) AS WAR
        FROM zips_WAR_hitters z
        JOIN zips_WAR_hitters_comp z2 USING (year, player_name, team_abb)
        LEFT JOIN current_rosters r USING (player_name, year)
        LEFT JOIN teams t USING (team_id, year)
        WHERE 1
            AND z.year = %s
        HAVING 1
        ORDER BY WAR DESC
    ) a
    LEFT JOIN name_mapper nm ON (1
        AND a.player_name = nm.wrong_name
        AND (nm.start_year IS NULL OR nm.start_year <= a.year)
        AND (nm.end_year IS NULL OR nm.end_year >= a.year)
        # AND (nm.position = '' OR nm.position = a.position)
        # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
        # AND (nm.nsbl_team = '' OR nm.nsbl_team = a.team_abb)
    )
    LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
        AND nm.right_lname = nm2.right_lname
        AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
        AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
        AND (nm.position = '' OR nm.position = nm2.position)
        AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
    )
    LEFT JOIN(
        SELECT year
        , player_name
        , team_abb AS current_team
        , salary
        , contract_year
        , expires
        , NTC
        , position
        FROM excel_rosters
        JOIN (
            SELECT year
            , MAX(date) AS date
            FROM excel_rosters
            WHERE 1
                AND year = %s
        ) cur USING (year, date)
    ) cre ON (1
        AND (cre.position != 'p'
            OR cre.player_name in ('Shohei Ohtani', 'Brendan McKay', 'Michael Lorenzen')
        )
        AND IFNULL(nm2.wrong_name, a.player_name) = cre.player_name
    )
    LEFT JOIN teams t ON (cre.current_team = t.spreadsheet_abb AND cre.year = t.year)
    GROUP BY year, position, COALESCE(CONCAT(nm2.right_fname, ' ', nm2.right_lname), a.player_name)
    ;"""

    query = qry % (year, year)

    res = db.query(query)

    csv_title = os.getcwd() + "/HIDDEN_FreeAgentBatters.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Player Name", "RL Team", "NSBL Team", 
    "Salary", "Contract Year", "Contract Expires", "NTC",
    "Age", "Position", "Bats", "Park", 
    "Position_Adj", "Range", "Error", "Arm", "Passed_Ball", "DRS", "dWAR", 
    "vsL_wRC+", "vsR_wRC+", 
    "BABIP", "OPS+", "wRC+",
    "vsL_oWAR", "vsR_oWAR", "oWAR",
    "vsL_WAR", "vsR_WAR", "WAR"]
    append_csv.writerow(csv_header)

    for row in res:
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_hidden_FA_pitchers(year):
    print "\t hidden FA pitchers"
    qry = """SELECT a.year
    , COALESCE(CONCAT(nm2.right_fname, ' ', nm2.right_lname), a.player_name) AS player_name
    , a.team_abb
    , IFNULL(MAX(t.team_name), "FREE AGENT") AS team
    , MAX(cre.salary) AS salary
    , MAX(cre.contract_year) AS contract_year
    , MAX(cre.expires) AS expires
    , MAX(cre.NTC) AS NTC
    , a.age
    , a.g
    , a.gs
    , a.ip
    , a.k_9
    , a.bb_9
    , a.k_bb
    , a.hr_9
    , a.k_pct
    , a.bb_pct
    , a.k_bb_pct
    , a.hr_pct
    , a.park_FIP
    , a.park_ERA
    , a.FIP_minus
    , a.ERA_minus
    , a.FIP_WAR
    , a.ERA_WAR
    , a.Scaled_FIP_WAR
    , a.Scaled_ERA_WAR
    , a.vsL_BABIP
    , a.vsL_OPS_plus
    , a.vsL_wRC_plus
    , a.vsR_BABIP
    , a.vsR_OPS_plus
    , a.vsR_wRC_plus
    FROM(
        SELECT year
        , player_name
        , z.team_abb
        , t.team_abb AS nsbl_roster
        , z.age
        , p.g
        , p.gs
        , z.ip
        , FORMAT(k_9,1) AS k_9
        , FORMAT(bb_9,1) AS bb_9
        , FORMAT(k_bb,1) AS k_bb
        , FORMAT(hr_9,1) AS hr_9
        , CONCAT( FORMAT(100*(pct.k_pct),1), "%%") AS k_pct
        , CONCAT( FORMAT(100*(pct.bb_pct),1), "%%") AS bb_pct
        , CONCAT( FORMAT(100*(pct.k_bb_pct),1), "%%") AS k_bb_pct
        , CONCAT( FORMAT(100*(pct.hr_pct),1), "%%") AS hr_pct
        , FORMAT(park_FIP,2) AS park_FIP
        , FORMAT(park_ERA,2) AS park_ERA
        , FORMAT(FIP_minus,1) AS FIP_minus
        , FORMAT(ERA_minus,1) AS ERA_minus
        , FORMAT(FIP_WAR,2) AS FIP_WAR
        , FORMAT(ERA_WAR,2) AS ERA_WAR
        , IF(p.gs>=3, FORMAT((FIP_WAR/z.ip)*180,2), FORMAT((FIP_WAR/z.ip)*65,2)) AS Scaled_FIP_WAR
        , IF(p.gs>=3, FORMAT((ERA_WAR/z.ip)*180,2), FORMAT((ERA_WAR/z.ip)*65,2)) AS Scaled_ERA_WAR
        , RIGHT(FORMAT(z2.babip,3),4) AS 'vsL_BABIP'
        , FORMAT(z2.OPS_plus_against,1) AS 'vsL_OPS_plus'
        , FORMAT(z2.wRC_plus_against,1) AS 'vsL_wRC_plus'
        , RIGHT(FORMAT(z3.babip,3),4) AS 'vsR_BABIP'
        , FORMAT(z3.OPS_plus_against,1) AS 'vsR_OPS_plus'
        , FORMAT(z3.wRC_plus_against,1) AS 'vsR_wRC_plus'
        FROM zips_WAR_pitchers z
        JOIN zips_WAR_pitchers_comp z2 USING (player_name, year)
        JOIN zips_WAR_pitchers_comp z3 USING (player_name, year)
        JOIN(
            SELECT 
            year, player_name, SUM(so)/SUM(ab+bb+hbp) AS k_pct,SUM(bb)/SUM(ab+bb+hbp) AS BB_pct,SUM(so-bb)/SUM(ab+bb+hbp) AS k_bb_pct, SUM(hr)/SUM(ab+bb+hbp) AS hr_pct
            FROM zips_pitching_splits
            GROUP BY year, player_name
        ) pct USING (player_name, year)
        JOIN zips_pitching p USING (player_name, year)
        LEFT JOIN current_rosters r USING (player_name, year)
        LEFT JOIN teams t USING (team_id, year)
        WHERE 1
            AND z.year = %s
            AND z2.vs_hand = 'L'
            AND z3.vs_hand = 'R'
    ) a
    LEFT JOIN name_mapper nm ON (1
        AND a.player_name = nm.wrong_name
        AND (nm.start_year IS NULL OR nm.start_year <= a.year)
        AND (nm.end_year IS NULL OR nm.end_year >= a.year)
        # AND (nm.position = '' OR nm.position = a.position)
        # AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
        # AND (nm.nsbl_team = '' OR nm.nsbl_team = a.team_abb)
    )
    LEFT JOIN name_mapper nm2 ON (nm.right_fname = nm2.right_fname
        AND nm.right_lname = nm2.right_lname
        AND (nm.start_year IS NULL OR nm.start_year = nm2.start_year)
        AND (nm.end_year IS NULL OR nm.end_year = nm2.end_year)
        AND (nm.position = '' OR nm.position = nm2.position)
        AND (nm.rl_team = '' OR nm.rl_team = nm2.rl_team)
    )
    LEFT JOIN(
        SELECT year
        , player_name
        , team_abb AS current_team
        , salary
        , contract_year
        , expires
        , NTC
        , position
        FROM excel_rosters
        JOIN (
            SELECT year
            , MAX(date) AS date
            FROM excel_rosters
            WHERE 1
                AND year = %s
        ) cur USING (year, date)
    ) cre ON (1
        AND (cre.position = 'p'
            OR cre.player_name in ('Caleb Joseph', 'Donnie Dewees', 'Javier Guerra', 'John Nogowski', 'Kaleb Cowart', 'Russell Martin')
        )
        AND IFNULL(nm2.wrong_name, a.player_name) = cre.player_name
    )
    LEFT JOIN teams t ON (cre.current_team = t.spreadsheet_abb AND cre.year = t.year)
    GROUP BY year, COALESCE(CONCAT(nm2.right_fname, ' ', nm2.right_lname), a.player_name)
    ;"""

    query = qry % (year, year)

    res = db.query(query)

    csv_title = os.getcwd() + "/HIDDEN_FreeAgentPitchers.csv"
    csv_file = open(csv_title, "wb")
    append_csv = csv.writer(csv_file)
    csv_header = ["Player Name", "RL Team", "NSBL Team", 
    "Salary", "Contract Year", "Contract Expires", "NTC",
    "Age", "G", "GS", "Innings",
    "K/9", "BB/9", "K/BB", "HR/9",
    "K%", "BB%", "K-BB%", "HR%",
    "pFIP", "pERA", "FIP-", "ERA-",
    "FIP_WAR", "ERA_WAR", 
    "Scaled_FIP_WAR", "Scaled_ERA_WAR",
    "vsL_BABIP", "vsL_OPS+", "vsL_wRC+",
    "vsR_BABIP", "vsR_OPS+", "vsR_wRC+"]
    append_csv.writerow(csv_header)

    for row in res:
        # raw_input(row)
        row = list(row[1:])
        for i, val in enumerate(row):
            if type(val) in (str,):
                row[i] = "".join([l if ord(l) < 128 else "" for l in val])
        append_csv.writerow(row)

def export_hidden_value(year):
    for t_name, table in {
            "trade_value_players": "_trade_value", 
            "trade_value_teams": "_trade_value_teams",
        }.items():

        print "\t " + str(t_name)

        path_base = os.getcwd()

        csv_title = path_base + "/HIDDEN_%s.csv" % (t_name)
        csv_file = open(csv_title, "wb")
        append_csv = csv.writer(csv_file)
        csv_header = []

        qry = """SELECT a.*
        FROM %s a
        JOIN(
            SELECT year, MAX(season_gp) AS season_gp
            FROM %s
            WHERE year = %s
        ) b USING (year, season_gp)
        WHERE year = %s;"""

        query = qry % (table, table, year, year)
        # raw_input(query)

        res = db.query(query)

        col_names_qry = """SELECT `COLUMN_NAME` 
        FROM `INFORMATION_SCHEMA`.`COLUMNS` 
        WHERE `TABLE_SCHEMA`='NSBL' 
        AND `TABLE_NAME`='%s';"""

        col_names_query = col_names_qry % (table)

        col_names = db.query(col_names_query)

        for cn in col_names:
            csv_header.append(cn[0])

        append_csv.writerow(csv_header)

        for row in res:
            row = list(row)
            for i, val in enumerate(row):
                if type(val) in (str,):
                    row[i] = "".join([l if ord(l) < 128 else "" for l in val])
            append_csv.writerow(row)


if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2020)

    args = parser.parse_args()
    
    initiate(args.year)

