from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import numpy as np
import math
from scipy.stats import norm as NormDist, binom as BinomDist


# script that estimates playoff probabilities based on both optimized and projected roster strength and variance. it then bootstraps to estimate probabilities of round advancements using the log5 odds ratio and binomial probability mass function to find the odds of winning a 5/7 game series


db = db('NSBL')


def process(year):
    start_time = time()

    process_basic(year)
    process_matrix(year)
    process_division(year)
    process_top_seed(year)
    process_wc1(year)
    process_wc2(year)
    process_win_wc(year)
    process_ds(year)
    process_cs(year)
    process_ws(year)
    process_champion(year)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "playoff_probabilities.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def process_basic(year):
    print 'initial table setup'
    for _type in ('roster', 'projected'):

        basic_query = """SELECT
        team_abb, team_name,
        year, season_gp, games_played, current_W, current_L,
        overall_var,
        roster_W, roster_L, roster_pct,
        ros_W, ros_L, ros_pct,
        projected_W, projected_L, projected_pct
        FROM __team_strength t1
        JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __team_strength GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
        WHERE year = %s;"""

        basic_query = basic_query % (year)

        # raw_input(basic_query)

        basic_res = db.query(basic_query)

        for basic_row in basic_res:
            entry = {}
            team_abb, team_name, year, season_gp, games_played, cur_W, cur_L, overall_var, roster_W, roster_L, roster_pct, ros_W, ros_L, ros_pct, projected_W, projected_L, projected_pct = basic_row

            games_played = float(games_played)
            games_remaining = float(max(0.0, 162.0 - games_played))

            # linearly scaled variance (no variance at game 162, full variance at game 0)
            projected_var = max(0.001, float(overall_var)*(games_remaining/162.0))

            projected_std =  max(0.001, math.sqrt(float(overall_var))*(games_remaining/162.0))


            division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name, year)

            if _type == 'roster':
                p_95 = float(roster_W) + 1.96*math.sqrt(float(overall_var))
                p_75 = float(roster_W) + 1.15*math.sqrt(float(overall_var))
                p_25 = float(roster_W) - 1.15*math.sqrt(float(overall_var))
                p_05 = float(roster_W) - 1.96*math.sqrt(float(overall_var))
                entry['team_abb'] = team_abb
                entry['team_name'] = team_name
                entry['year'] = year
                entry['season_gp'] = season_gp
                entry['games_played'] = games_played
                entry['division'] = division
                entry['strength_type'] = _type
                entry['strength_pct'] = roster_pct
                entry['var'] = overall_var
                entry['mean_W'] = roster_W
                entry['mean_L'] = roster_L
                entry['p_95'] = p_95
                entry['p_75'] = p_75
                entry['p_25'] = p_25
                entry['p_05'] = p_05

            elif _type == 'projected':
                p_95 = float(projected_W) + 1.96*(projected_std)
                p_75 = float(projected_W) + 1.15*(projected_std)
                p_25 = float(projected_W) - 1.15*(projected_std)
                p_05 = float(projected_W) - 1.96*(projected_std)

                entry['team_abb'] = team_abb
                entry['team_name'] = team_name
                entry['year'] = year
                entry['season_gp'] = season_gp
                entry['games_played'] = games_played
                entry['division'] = division
                entry['strength_type'] = _type
                entry['strength_pct'] = ros_pct
                entry['var'] = projected_var
                entry['mean_W'] = projected_W
                entry['mean_L'] = projected_L
                entry['p_95'] = p_95
                entry['p_75'] = p_75
                entry['p_25'] = p_25
                entry['p_05'] = p_05


            db.insertRowDict(entry, '__playoff_probabilities', insertMany=False, replace=True, rid=0,debug=1)
            db.conn.commit()


def process_matrix(year):
    print 'matchup matrix'
    entries = []
    for _type in ('roster', 'projected'):
        qry = """SELECT
        team_abb, strength_pct, year, games_played, season_gp
        FROM __playoff_probabilities
        JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
        WHERE strength_type = '%s'
        AND year = %s;"""

        query = qry % (_type, year)

        # raw_input(query)
        res = db.query(query)

        for row in res:

            team_abb, strength_pct, year, games_played, season_gp = row

            oppn_qry = """SELECT
            team_abb, strength_pct, year, games_played
            FROM __playoff_probabilities
            JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
            WHERE strength_type = '%s'
            AND team_abb != '%s'
            AND year = %s;"""

            oppn_query = oppn_qry % (_type, team_abb, year)

            # print oppn_query
            oppn_res = db.query(oppn_query)

            for row in oppn_res:
                entry = {}
                oppn_abb, opponent_strength_pct, oppn_year, oppn_games_played = row
                entry['team_abb'] = team_abb
                entry['year'] = year
                entry['season_gp'] = season_gp
                entry['games_played'] = games_played
                entry['opponent'] = oppn_abb
                entry['strength_type'] = _type

                strength_pct, opponent_strength_pct = float(strength_pct), float(opponent_strength_pct)

                odds = ((strength_pct - strength_pct*opponent_strength_pct)/(strength_pct + opponent_strength_pct - 2*strength_pct*opponent_strength_pct))

                entry['odds_ratio'] = odds

                entries.append(entry)

    db.insertRowDict(entries, '__matchup_matrix', insertMany=True, replace=True, rid=0,debug=1)
    db.conn.commit()


def process_division(year):
    print 'division'
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for div in ('AL East', 'AL Central', 'AL West', 'NL East', 'NL Central', 'NL West'):

            qry = """SELECT 
            team_abb, team_name, 
            mean_W/162.0, var, year, games_played
            FROM __playoff_probabilities
            JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
            WHERE strength_type = '%s'
            AND division = '%s'
            AND year = %s;"""
            query = qry % (_type, div, year)

            # raw_input(query)

            res = db.query(query)

            div_dict = {}
            for row in res:
                team_abb, team_name, strength_pct, var, year, games_played = row
                # print '\t\t', team_name

                if games_played > 162:
                    strength_pct = float((float(strength_pct)*162.0)/float(games_played))
                else:
                    strength_pct = float(strength_pct)

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name, year)

                win_division_prob = np.prod(get_probabilities(team_name, div_teams, strength_pct, games_played, float(var), _type, year)[0])

                div_dict[team_name] = [win_division_prob, 1.0, False, year, games_played]

            col_name = 'win_division'
            adjust_probabilities(div_dict, col_name, 1.0, _type)


def process_top_seed(year):
    print "top seed"

    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):
            team_qry = """SELECT 
            team_abb, team_name, win_division,
            mean_W/162.0, var, year, games_played
            FROM __playoff_probabilities
            JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
            WHERE strength_type = '%s' 
            AND LEFT(division,2) = '%s'
            AND year = %s;"""
            team_query = team_qry % (_type, conf, year)
            # raw_input(team_query)
            team_res = db.query(team_query)

            top_dict = {}
            for team_row in team_res:
                team_abb, team_name, max_prob, strength_pct, var, year, games_played = team_row
                max_prob = float(max_prob)
                # print '\t\t', team_name

                if games_played > 162:
                    strength_pct = float((float(strength_pct)*162.0)/float(games_played))
                else:
                    strength_pct = float(strength_pct)

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name, year)

                top_seed_prob = np.prod(get_probabilities(team_name, conf_teams, strength_pct, games_played, float(var), _type, year)[0])

                top_dict[team_name] = [top_seed_prob, max_prob, False, year, games_played]

            col_name = 'top_seed'
            adjust_probabilities(top_dict, col_name, 1.0, _type)


def process_wc1(year):
    print 'wc1'
    for _type in ('roster', 'projected'):
        print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, win_division, mean_W/162.0, var, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND LEFT(division,2) = '%s' AND year = %s" % (_type, conf, year)

            # raw_input(team_query)

            team_res = db.query(team_query)

            wc_dict = {}
            for team_row in team_res:
                team_abb, team_name, div_prob, strength_pct, var, year, games_played = team_row
                print '\t\t', team_name

                if games_played > 162:
                    strength_pct = float((float(strength_pct)*162.0)/float(games_played))
                else:
                    strength_pct = float(strength_pct)

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name, year)

                div_winners_qry = """SELECT 
                p1.team_name,
                p2.team_name,
                p3.team_name, 
                (p1.win_division)*(p2.win_division)*(p3.win_division)
                FROM __playoff_probabilities p1
                JOIN __playoff_probabilities p2
                JOIN __playoff_probabilities p3
                JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t1 ON (p1.team_abb=t1.team_abb AND p1.year=t1.year AND  p1.games_played=t1.games_played)
                JOIN (SELECT team_abb, MAX(YEAR) AS YEAR, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 ON (p2.team_abb=t2.team_abb AND p2.year=t2.year AND  p2.games_played=t2.games_played)
                JOIN (SELECT team_abb, MAX(YEAR) AS YEAR, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t3 ON (p3.team_abb=t3.team_abb AND p3.year=t3.year AND  p3.games_played=t3.games_played)
                WHERE 1
                AND p1.strength_type = '%s'
                AND p2.strength_type = '%s'
                AND p3.strength_type = '%s'
                AND p1.division = '%s West'
                AND p2.division = '%s Central'
                AND p3.division = '%s East'
                AND p1.team_name != '%s'
                AND p2.team_name != '%s'
                AND p3.team_name != '%s'
                AND p1.year = %s
                AND p2.year = %s
                AND p3.year = %s;"""

                div_winners_query = div_winners_qry % (_type, _type, _type, conf, conf, conf, team_name, team_name, team_name, year, year, year)
                # raw_input(div_winners_query)
                div_winners_res = db.query(div_winners_query)

                wc_pre_prob = float(0.0)
                for div_row in div_winners_res:
                    div1_team, div2_team, div3_team, situation_prob = div_row

                    set_teams = []
                    for tm in conf_teams:
                        if tm not in (div1_team, div2_team, div3_team):
                            set_teams.append(tm)

                    win_wc_prob = np.prod(get_probabilities(team_name, set_teams, strength_pct, games_played, float(var), _type, year)[0])

                    wc_pre_prob += (float(situation_prob)*float(win_wc_prob))

                wc_pre_prob = wc_pre_prob*(1.0-float(div_prob))
                wc_dict[team_name] = [wc_pre_prob,(1.0-float(div_prob)),False, year, games_played]

            col_name = 'wc_1'
            adjust_probabilities(wc_dict, col_name, 1.0, _type)


def process_wc2(year):
    print "wc2"
    for _type in ('roster', 'projected'):
        print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, (win_division+wc_1), mean_W/162.0, var, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND LEFT(division,2) = '%s'AND year = %s" % (_type, conf, year)

            team_res = db.query(team_query)

            wc2_dict = {}
            for team_row in team_res:
                team_abb, team_name, po_prob, strength_pct, var, year, games_played = team_row
                print '\t\t', team_name

                if games_played > 162:
                    strength_pct = float((float(strength_pct)*162.0)/float(games_played))
                else:
                    strength_pct = float(strength_pct)

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name, year)

                div_winners_qry = """SELECT 
                p1.team_name,
                p2.team_name,
                p3.team_name,
                p4.team_name,
                (p1.win_division+p1.wc_1)*(p2.win_division+p2.wc_1)*(p3.win_division+p3.wc_1)*(p4.win_division+p4.wc_1)
                FROM __playoff_probabilities p1
                JOIN __playoff_probabilities p2
                JOIN __playoff_probabilities p3
                JOIN __playoff_probabilities p4
                JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t1 ON (p1.team_abb=t1.team_abb AND p1.year=t1.year AND  p1.games_played=t1.games_played)
                JOIN (SELECT team_abb, MAX(YEAR) AS YEAR, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 ON (p2.team_abb=t2.team_abb AND p2.year=t2.year AND  p2.games_played=t2.games_played)
                JOIN (SELECT team_abb, MAX(YEAR) AS YEAR, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t3 ON (p3.team_abb=t3.team_abb AND p3.year=t3.year AND  p3.games_played=t3.games_played)
                JOIN (SELECT team_abb, MAX(YEAR) AS YEAR, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t4 ON (p4.team_abb=t4.team_abb AND p4.year=t4.year AND  p4.games_played=t4.games_played)
                WHERE 1
                AND p1.strength_type = '%s'
                AND p2.strength_type = '%s'
                AND p3.strength_type = '%s'
                AND p4.strength_type = '%s'
                AND p1.division = '%s West'
                AND p2.division = '%s Central'
                AND p3.division = '%s East'
                AND LEFT(p4.division,2) = '%s'
                AND p1.team_name != '%s'
                AND p2.team_name != '%s'
                AND p3.team_name != '%s'
                AND p4.team_name != '%s'
                AND p1.team_name != p4.team_name
                AND p2.team_name != p4.team_name
                AND p3.team_name != p4.team_name
                AND p1.year = %s
                AND p2.year = %s
                AND p3.year = %s
                AND p4.year = %s;"""

                div_winners_query = div_winners_qry % (_type, _type, _type, _type, conf, conf, conf, conf, team_name, team_name, team_name, team_name, year, year, year, year)
                div_winners_res = db.query(div_winners_query)

                wc2_pre_prob = float(0.0)
                for div_row in div_winners_res:
                    div1_team, div2_team, div3_team, div4_team, situation_prob = div_row

                    set_teams = []
                    for tm in conf_teams:
                        if tm not in (div1_team, div2_team, div3_team, div4_team):
                            set_teams.append(tm)

                    win_wc2_prob = np.prod(get_probabilities(team_name, set_teams, strength_pct, games_played, float(var), _type, year)[0])

                    wc2_pre_prob += (float(situation_prob)*float(win_wc2_prob))

                wc2_pre_prob = wc2_pre_prob*(1.0-float(po_prob))
                wc2_dict[team_name] = [wc2_pre_prob,(1.0-float(po_prob)),False, year, games_played]

            col_name = 'wc_2'
            adjust_probabilities(wc2_dict, col_name, 1.0, _type)


def process_win_wc(year):
    print "win wild card"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, win_division, wc_1, wc_2, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND LEFT(division,2) = '%s' AND year = %s" % (_type, conf, year)
            team_res = db.query(team_query)

            adv_dict = {}
            for team_row in team_res:
                team_abb, team_name, div_prob, wc1_prob, wc2_prob, year, games_played = team_row
                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, wc_1, wc_2
                FROM __playoff_probabilities
                JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
                WHERE strength_type = '%s' 
                AND LEFT(division,2) = '%s'
                AND team_name != '%s'
                AND year = %s;"""
                oppn_query = oppn_qry % (_type, conf, team_name, year)
                oppn_res = db.query(oppn_query)

                wc_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_wc1, oppn_wc2 = oppn_row

                    # probability of wc1 * (oppn_wc2 | not wc2)
                    if (1.0-float(wc2_prob)) == 0:
                        matchup1_prob = 0.0
                    else:
                        matchup1_prob = float(wc1_prob*oppn_wc2)/(1.0-float(wc2_prob))

                    # probability of wc2 * (oppn_wc1 | not wc1)
                    if (1.0-float(wc1_prob)) == 0:
                        matchup2_prob = 0.0
                    else:
                        matchup2_prob = float(wc2_prob*oppn_wc1)/(1.0-float(wc1_prob))

                    matchup_prob = matchup1_prob + matchup2_prob

                    win_game_prob = get_single_game_win_prob(team_abb, oppn_abb, _type, year)

                    wc_overall_prob = matchup_prob*win_game_prob

                    wc_prob += wc_overall_prob

                overall_prob = wc_prob
                adv_dict[team_name] = [overall_prob, 1.0, False, year, games_played]

            col_name = 'win_wc'
            adjust_probabilities(adv_dict, col_name, 1.0, _type)


def process_ds(year):
    print "make division series"

    for _type in ('roster', 'projected'):
        # print '\t', _type

        query = "SELECT team_abb, team_name, win_division+win_wc, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND year = %s;" % (_type, year)
        res = db.query(query)

        col_name = 'make_ds'
        for row in res:
            team_abb, team_name, div_prob, year, games_played = row
            db.updateRow({col_name:div_prob},"__playoff_probabilities",("team_name","strength_type","year",
            "games_played"),(team_name,_type,year,games_played),operators=['=','=','=','='])
            db.conn.commit()


def process_cs(year):
    print "make championship series"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, division, top_seed, win_division, win_wc, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND LEFT(division,2) = '%s' AND year = %s" % (_type, conf, year)
            # raw_input(team_query)
            team_res = db.query(team_query)

            cs_dict = {}
            for team_row in team_res:
                team_abb, team_name, team_division, top_seed, win_div, win_wc, year, games_played = team_row

                win_2_3_seed = float(win_div)-float(top_seed)

                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, top_seed, win_division, win_wc, (win_division-top_seed) AS 'middle_seed'
                FROM __playoff_probabilities
                JOIN (SELECT team_abb, MAX(YEAR) AS 'year', MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) a USING (team_abb, YEAR, games_played)
                WHERE strength_type = '%s' 
                AND LEFT(division,2) = '%s'
                AND team_name != '%s'
                AND year = %s;"""
                oppn_query = oppn_qry % ( _type, conf, team_name, year)
                # raw_input(oppn_query)
                oppn_res = db.query(oppn_query)

                cs_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_top, oppn_div, oppn_wc, oppn_2_3_seed = oppn_row


                    # probability of top_seed * (oppn_wc | not wc)
                    if (1.0-float(win_wc)) == 0:
                        matchup1_prob = 0.0
                    else:
                        matchup1_prob = float(top_seed*oppn_wc)/(1.0-float(win_wc))

                    # probability of wc * (oppn_top_seed | not top_seed)
                    if (1.0-float(top_seed)) == 0:
                        matchup2_prob = 0.0
                    else:
                        matchup2_prob = float(win_wc*oppn_top)/(1.0-float(top_seed))

                    matchup3_prob = float(win_2_3_seed)*float(oppn_2_3_seed)

                    matchup_prob = matchup1_prob + matchup2_prob + matchup3_prob

                    win_game_prob = get_single_game_win_prob(team_abb, oppn_abb, _type, year)
                    series_games = 5
                    win_series = get_series_prob(series_games=series_games, series_wins=0, series_losses=0, team_winProb=win_game_prob)

                    cs_overall_prob = matchup_prob*win_series

                    cs_prob += cs_overall_prob

                overall_prob = cs_prob
                cs_dict[team_name] = [overall_prob, 1.0, False, year, games_played]

            col_name = 'make_cs'
            adjust_probabilities(cs_dict, col_name, 2.0, _type)


def process_ws(year):
    print "make world series"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, make_cs, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND LEFT(division,2) = '%s' AND year = %s" % (_type, conf, year)
            team_res = db.query(team_query)

            ws_dict = {}
            for team_row in team_res:
                team_abb, team_name, make_cs, year, games_played = team_row

                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, make_cs
                FROM __playoff_probabilities
                JOIN (SELECT team_abb, MAX(YEAR) AS 'year', MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) a USING (team_abb, YEAR, games_played)
                WHERE strength_type = '%s'
                AND LEFT(division,2) = '%s'
                AND team_name != '%s'
                AND year = %s;"""
                oppn_query = oppn_qry % (_type, conf, team_name, year)
                oppn_res = db.query(oppn_query)

                ws_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_cs = oppn_row

                    matchup_prob = float(make_cs)*float(oppn_cs)

                    win_game_prob = get_single_game_win_prob(team_abb, oppn_abb, _type, year)
                    series_games = 7
                    win_series = get_series_prob(series_games=series_games, series_wins=0, series_losses=0, team_winProb=win_game_prob)

                    ws_overall_prob = matchup_prob*win_series

                    ws_prob += ws_overall_prob

                overall_prob = ws_prob
                ws_dict[team_name] = [overall_prob, 1.0, False, year, games_played]

            col_name = 'make_ws'
            adjust_probabilities(ws_dict, col_name, 1.0, _type)


def process_champion(year):
    print "win world series"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        champ_dict = {}
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, make_ws, year, games_played FROM __playoff_probabilities JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE strength_type = '%s' AND LEFT(division,2) = '%s' AND year = %s" % (_type, conf, year)
            team_res = db.query(team_query)

            for team_row in team_res:
                team_abb, team_name, make_ws, year, games_played = team_row

                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, make_ws
                FROM __playoff_probabilities
                JOIN (SELECT team_abb, MAX(YEAR) AS 'year', MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) a USING (team_abb, YEAR, games_played)
                WHERE strength_type = '%s'
                AND LEFT(division,2) != '%s'
                AND year = %s;"""
                oppn_query = oppn_qry % (_type, conf, year)

                # raw_input(oppn_query)
                oppn_res = db.query(oppn_query)

                champ_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_ws = oppn_row

                    matchup_prob = float(make_ws)*float(oppn_ws)

                    win_game_prob = get_single_game_win_prob(team_abb, oppn_abb, _type, year)
                    series_games = 7
                    win_series = get_series_prob(series_games=series_games, series_wins=0, series_losses=0, team_winProb=win_game_prob)

                    champ_overall_prob = matchup_prob*win_series

                    champ_prob += champ_overall_prob

                overall_prob = champ_prob
                champ_dict[team_name] = [overall_prob, 1.0, False, year, games_played]

        col_name = 'win_ws'
        adjust_probabilities(champ_dict, col_name, 1.0, _type)


def get_series_prob(series_games, series_wins, series_losses, team_winProb):
    team_probs = []

    if series_wins == series_games/2+1:
        team_probs.append(1)
        total_games = series_wins+series_losses

    if series_losses == series_games/2+1:
        team_probs.append(0)

    if (series_wins != series_games/2+1 and series_losses != series_games/2+1):
        for end_game in range(series_games/2+1, series_games+1-series_losses):
            team_in_N = BinomDist.pmf(n=end_game-1-series_wins, k=(series_games/2-series_wins), p=team_winProb) * team_winProb

            team_probs.append(team_in_N)

    return float(sum(team_probs))


def get_single_game_win_prob(team1_abb, team2_abb, strength_type, year):
    team1_win_game_query = "SELECT odds_ratio FROM __matchup_matrix JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __matchup_matrix GROUP BY team_abb, year) t2 USING (team_abb, year, games_played) WHERE team_abb = '%s' AND opponent = '%s' AND strength_type = '%s' AND year = %s" % (team1_abb, team2_abb, strength_type, year)

    return float(db.query(team1_win_game_query)[0][0])


def adjust_probabilities(prob_dict, col_name, sum_to, _type):
    bool_temp = False
    final_vals = {}
    while bool_temp is False:
        bool_temp = True

        prob_sum = 0.0
        for tm, values in prob_dict.items():
            curr_prob, max_prob, tm_bool, year, games_played = values
            if tm_bool is False:
                prob_sum += curr_prob

        prob_factor = prob_sum/sum_to

        for tm, values in prob_dict.items():
            curr_prob, max_prob, tm_bool, year, games_played = values

            if prob_factor == 0:
                adj_val = curr_prob
            else:
                adj_val = curr_prob/prob_factor

            if (adj_val > max_prob and tm_bool is False):
                sum_to = sum_to - max_prob
                bool_temp = False
                prob_dict[tm] = [curr_prob, max_prob, True, year, games_played]
                final_vals[tm] = [max_prob, year, games_played]

            elif tm_bool is True:
                final_vals[tm] = [max_prob, year, games_played]
            else:
                prob_dict[tm] = [curr_prob, max_prob, False, year, games_played]
                final_vals[tm] = [adj_val, year, games_played]

    for tm, vals in final_vals.items():
        val, year, games_played = vals
        db.updateRow({col_name:val},"__playoff_probabilities",("team_name","strength_type","year","games_played"),(tm,_type,year,games_played),operators=['=','=','=','='])
        db.conn.commit()


def get_probabilities(team_name, oppn_teams, strength_pct, games_played, projected_var, _type, year):
    prob_list = []
    prob_name_list = []
    for opponent in oppn_teams:
        oppn_entry = {}
        qry = """SELECT p.mean_W, p.var, year, games_played
        FROM __team_strength
        JOIN __playoff_probabilities p USING (team_abb, team_name, year, games_played)
        JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
        WHERE strength_type = '%s'
        AND team_name = '%s'
        AND year = %s;"""
        query = qry % (_type, opponent, year)

        # if _type == 'projected':
            # raw_input(query)
        res = db.query(query)

        oppn_W, oppn_var, oppn_year, oppn_games_played = res[0]

        
        team_W = strength_pct*162
        oppn_W = oppn_W

        diff_W = float(team_W) - float(oppn_W)
        diff_std = math.sqrt(float(projected_var) + float(oppn_var))

        # the probability that the team will finish with a better record than the opponent
        dist_prob = 1.0 - NormDist(loc=diff_W, scale=diff_std).cdf(0)

        oppn_entry[opponent] = dist_prob

        prob_name_list.append(oppn_entry)
        prob_list.append(dist_prob)


    return prob_list, prob_name_list


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2020)
    args = parser.parse_args()
    
    process(args.year)
    

