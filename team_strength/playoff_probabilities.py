from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time
import numpy as np
import math
from scipy.stats import norm as NormDist, binom as BinomDist

# script that estimates playoff probabilities based on both optimized and projected roster strength and variance. it then bootstrapps to estimate probabilities of round advancements using the log5 odds ratio and binomial probability mass function to find the odds of winning a 5/7 game series


db = db('NSBL')


def process():
    start_time = time()

    # Each time we run this, we clear the pre-existing tables
    db.query("TRUNCATE TABLE `__playoff_probabilities`")
    db.query("TRUNCATE TABLE `__matchup_matrix`")
    process_basic()
    process_matrix()
    process_division()
    process_top_seed()
    process_wc1()
    process_wc2()
    process_win_wc()
    process_ds()
    process_cs()
    process_ws()
    process_champion()

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "playoff_probabilities.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)

def process_basic():
    print 'initial table setup'
    for _type in ('roster', 'projected'):

        basic_query = """SELECT
        team_abb, team_name,
        roster_std,
        roster_W, roster_L, roster_pct,
        ros_W, ros_L, ros_pct,
        projected_W, projected_L, projected_pct
        FROM __team_strength"""

        basic_res = db.query(basic_query)

        for basic_row in basic_res:
            entry = {}
            team_abb, team_name, roster_std, roster_W, roster_L, roster_pct, ros_W, ros_L, ros_pct, projected_W, projected_L, projected_pct = basic_row

            games_remaining = float(ros_W) + float(ros_L)
            games_played = 162.0 - games_remaining
            # scaled quadradtic function mapping for std left in season:
            # std_left = roster_std*((x+162)(x-162)/162^2), where x is games_played
            projected_std = -float(roster_std)*(((float(games_played)+162.0)*(float(games_played)-162.0))/(162.0**2))

            division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name)

            if _type == 'roster':
                entry['team_abb'] = team_abb
                entry['team_name'] = team_name
                entry['division'] = division
                entry['strength_type'] = _type
                entry['strength_pct'] = roster_pct
                entry['std'] = roster_std
                entry['mean_W'] = roster_W
                entry['mean_L'] = roster_L

            elif _type == 'projected':
                entry['team_abb'] = team_abb
                entry['team_name'] = team_name
                entry['division'] = division
                entry['strength_type'] = _type
                entry['strength_pct'] = ros_pct
                entry['std'] = projected_std
                entry['mean_W'] = projected_W
                entry['mean_L'] = projected_L

            db.insertRowDict(entry, '__playoff_probabilities', insertMany=False, replace=True, rid=0,debug=1)
            db.conn.commit()

def process_matrix():
    print 'matchup matrix'
    entries = []
    for _type in ('roster', 'projected'):
        qry = """SELECT
        team_abb, strength_pct
        FROM __playoff_probabilities
        WHERE strength_type = '%s';"""
        query = qry % (_type)

        res = db.query(query)

        for row in res:

            team_abb, strength_pct = row

            oppn_qry = """SELECT
            team_abb, strength_pct
            FROM __playoff_probabilities
            WHERE strength_type = '%s'
            AND team_abb != '%s';"""

            oppn_query = oppn_qry % (_type, team_abb)

            oppn_res = db.query(oppn_query)

            for row in oppn_res:
                entry = {}
                oppn_abb, opponent_strength_pct = row
                entry['team_abb'] = team_abb
                entry['opponent'] = oppn_abb
                entry['strength_type'] = _type

                strength_pct, opponent_strength_pct = float(strength_pct), float(opponent_strength_pct)

                odds = ((strength_pct - strength_pct*opponent_strength_pct)/(strength_pct + opponent_strength_pct - 2*strength_pct*opponent_strength_pct))

                entry['odds_ratio'] = odds

                entries.append(entry)

    db.insertRowDict(entries, '__matchup_matrix', insertMany=True, replace=True, rid=0,debug=1)
    db.conn.commit()

def process_division():
    print 'division'
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for div in ('AL East', 'AL Central', 'AL West', 'NL East', 'NL Central', 'NL West'):

            qry = """SELECT 
            team_abb, team_name, 
            mean_W/162.0, std
            FROM __playoff_probabilities
            WHERE strength_type = '%s'
            AND division = '%s';"""
            query = qry % (_type, div)

            res = db.query(query)

            div_dict = {}
            for row in res:
                team_abb, team_name, strength_pct, std = row
                # print '\t\t', team_name

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name)

                win_division_prob = np.prod(get_probabilities(team_name, div_teams, float(strength_pct), float(std), _type)[0])

                div_dict[team_name] = [win_division_prob, 1.0, False]

            col_name = 'win_division'
            adjust_probabilities(div_dict, col_name, 1.0, _type)

def process_top_seed():
    print "top seed"

    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):
            team_qry = """SELECT 
            team_abb, team_name, win_division,
            mean_W/162.0, std
            FROM __playoff_probabilities
            WHERE strength_type = '%s' 
            AND LEFT(division,2) = '%s';"""
            team_query = team_qry % (_type, conf)
            team_res = db.query(team_query)

            top_dict = {}
            for team_row in team_res:
                team_abb, team_name, max_prob, strength_pct, std = team_row
                max_prob = float(max_prob)
                # print '\t\t', team_name

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name)

                top_seed_prob = np.prod(get_probabilities(team_name, conf_teams, float(strength_pct), float(std), _type)[0])

                top_dict[team_name] = [top_seed_prob, max_prob, False]

            col_name = 'top_seed'
            adjust_probabilities(top_dict, col_name, 1.0, _type)

def process_wc1():
    print 'wc1'
    for _type in ('roster', 'projected'):
        print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, win_division, mean_W/162.0, std FROM __playoff_probabilities WHERE strength_type = '%s' AND LEFT(division,2) = '%s'" % (_type, conf)

            team_res = db.query(team_query)

            wc_dict = {}
            for team_row in team_res:
                team_abb, team_name, div_prob, strength_pct, std = team_row
                print '\t\t', team_name

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name)

                div_winners_qry = """SELECT 
                p1.team_name,
                p2.team_name,
                p3.team_name, 
                (p1.win_division)*(p2.win_division)*(p3.win_division)
                FROM __playoff_probabilities p1
                JOIN __playoff_probabilities p2
                JOIN __playoff_probabilities p3
                WHERE 1
                AND p1.strength_type = '%s'
                AND p2.strength_type = '%s'
                AND p3.strength_type = '%s'
                AND p1.division = '%s West'
                AND p2.division = '%s Central'
                AND p3.division = '%s East'
                AND p1.team_name != '%s'
                AND p2.team_name != '%s'
                AND p3.team_name != '%s';"""

                div_winners_query = div_winners_qry % (_type, _type, _type, conf, conf, conf, team_name, team_name, team_name)
                div_winners_res = db.query(div_winners_query)

                wc_pre_prob = float(0.0)
                for div_row in div_winners_res:
                    div1_team, div2_team, div3_team, situation_prob = div_row

                    set_teams = []
                    for tm in conf_teams:
                        if tm not in (div1_team, div2_team, div3_team):
                            set_teams.append(tm)

                    win_wc_prob = np.prod(get_probabilities(team_name, set_teams, float(strength_pct), float(std), _type)[0])

                    wc_pre_prob += (float(situation_prob)*float(win_wc_prob))

                wc_pre_prob = wc_pre_prob*(1.0-float(div_prob))
                wc_dict[team_name] = [wc_pre_prob,(1.0-float(div_prob)),False]

            col_name = 'wc_1'
            adjust_probabilities(wc_dict, col_name, 1.0, _type)

def process_wc2():
    print "wc2"
    for _type in ('roster', 'projected'):
        print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, (win_division+wc_1), mean_W/162.0, std FROM __playoff_probabilities WHERE strength_type = '%s' AND LEFT(division,2) = '%s'" % (_type, conf)

            team_res = db.query(team_query)

            wc2_dict = {}
            for team_row in team_res:
                team_abb, team_name, po_prob, strength_pct, std = team_row
                print '\t\t', team_name

                division, div_teams, conf_teams, non_conf_teams = helper.get_division(team_name)

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
                AND p3.team_name != p4.team_name ;"""

                div_winners_query = div_winners_qry % (_type, _type, _type, _type, conf, conf, conf, conf, team_name, team_name, team_name, team_name)
                div_winners_res = db.query(div_winners_query)

                wc2_pre_prob = float(0.0)
                for div_row in div_winners_res:
                    div1_team, div2_team, div3_team, div4_team, situation_prob = div_row

                    set_teams = []
                    for tm in conf_teams:
                        if tm not in (div1_team, div2_team, div3_team, div4_team):
                            set_teams.append(tm)

                    win_wc2_prob = np.prod(get_probabilities(team_name, set_teams, float(strength_pct), float(std), _type)[0])

                    wc2_pre_prob += (float(situation_prob)*float(win_wc2_prob))

                wc2_pre_prob = wc2_pre_prob*(1.0-float(po_prob))
                wc2_dict[team_name] = [wc2_pre_prob,(1.0-float(po_prob)),False]

            col_name = 'wc_2'
            adjust_probabilities(wc2_dict, col_name, 1.0, _type)

def process_win_wc():
    print "win wild card"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, win_division, wc_1, wc_2 FROM __playoff_probabilities WHERE strength_type = '%s' AND LEFT(division,2) = '%s'" % (_type, conf)
            team_res = db.query(team_query)

            adv_dict = {}
            for team_row in team_res:
                team_abb, team_name, div_prob, wc1_prob, wc2_prob = team_row
                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, wc_1, wc_2
                FROM __playoff_probabilities
                WHERE strength_type = '%s' 
                AND LEFT(division,2) = '%s'
                AND team_name != '%s';"""
                oppn_query = oppn_qry % (_type, conf, team_name)
                oppn_res = db.query(oppn_query)

                wc_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_wc_1, oppn_wc2 = oppn_row

                    matchup_prob = float(wc1_prob*oppn_wc2 + wc2_prob*oppn_wc_1)

                    win_game_query = "SELECT odds_ratio FROM __matchup_matrix WHERE team_abb = '%s' AND opponent = '%s' AND strength_type = '%s'" % (team_abb, oppn_abb, _type)
                    win_game_prob = float(db.query(win_game_query)[0][0])

                    wc_overall_prob = matchup_prob*win_game_prob

                    wc_prob += wc_overall_prob

                overall_prob = wc_prob
                adv_dict[team_name] = [overall_prob, 1.0, False]

            col_name = 'win_wc'
            adjust_probabilities(adv_dict, col_name, 1.0, _type)

def process_ds():
    print "make division series"

    for _type in ('roster', 'projected'):
        # print '\t', _type

        query = "SELECT team_abb, team_name, win_division+win_wc FROM __playoff_probabilities WHERE strength_type = '%s';" % (_type)
        res = db.query(query)

        col_name = 'make_ds'
        for row in res:
            team_abb, team_name, div_prob = row
            db.updateRow({col_name:div_prob},"__playoff_probabilities",("team_name","strength_type"),(team_name,_type),operators=['=','='])
            db.conn.commit()

def process_cs():
    print "make championship series"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, top_seed, win_division, win_wc FROM __playoff_probabilities WHERE strength_type = '%s' AND LEFT(division,2) = '%s'" % (_type, conf)
            team_res = db.query(team_query)

            cs_dict = {}
            for team_row in team_res:
                team_abb, team_name, top_seed, win_div, win_wc = team_row

                win_2_3_seed = float(win_div)-float(top_seed)

                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, top_seed, win_division, win_wc
                FROM __playoff_probabilities
                WHERE strength_type = '%s' 
                AND LEFT(division,2) = '%s'
                AND team_name != '%s';"""
                oppn_query = oppn_qry % (_type, conf, team_name)
                oppn_res = db.query(oppn_query)

                cs_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_top, oppn_div, oppn_wc = oppn_row

                    oppn_2_3_seed = float(oppn_div)-float(oppn_top)

                    matchup_prob = float(top_seed)*float(oppn_wc) + float(win_wc)*float(oppn_top) + (float(win_2_3_seed)*float(oppn_2_3_seed))

                    win_game_query = "SELECT odds_ratio FROM __matchup_matrix WHERE team_abb = '%s' AND opponent = '%s' AND strength_type = '%s'" % (team_abb, oppn_abb, _type)
                    win_game_prob = float(db.query(win_game_query)[0][0])

                    win_in_3 = BinomDist.pmf(n=3, k=3, p=win_game_prob)
                    win_in_4 = BinomDist.pmf(n=3, k=2, p=win_game_prob)*win_game_prob
                    win_in_5 = BinomDist.pmf(n=4, k=2, p=win_game_prob)*win_game_prob

                    win_series = float(win_in_3) + float(win_in_4) + float(win_in_5)
                    cs_overall_prob = matchup_prob*win_series

                    cs_prob += cs_overall_prob

                overall_prob = cs_prob
                cs_dict[team_name] = [overall_prob, 1.0, False]

            col_name = 'make_cs'
            adjust_probabilities(cs_dict, col_name, 2.0, _type)

def process_ws():
    print "make world series"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, make_cs FROM __playoff_probabilities WHERE strength_type = '%s' AND LEFT(division,2) = '%s'" % (_type, conf)
            team_res = db.query(team_query)

            ws_dict = {}
            for team_row in team_res:
                team_abb, team_name, make_cs = team_row

                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, make_cs
                FROM __playoff_probabilities
                WHERE strength_type = '%s'
                AND LEFT(division,2) = '%s'
                AND team_name != '%s';"""
                oppn_query = oppn_qry % (_type, conf, team_name)
                oppn_res = db.query(oppn_query)

                ws_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_cs = oppn_row

                    matchup_prob = float(make_cs)*float(oppn_cs)

                    win_game_query = "SELECT odds_ratio FROM __matchup_matrix WHERE team_abb = '%s' AND opponent = '%s' AND strength_type = '%s'" % (team_abb, oppn_abb, _type)
                    win_game_prob = float(db.query(win_game_query)[0][0])

                    win_in_4 = BinomDist.pmf(n=4, k=4, p=win_game_prob)
                    win_in_5 = BinomDist.pmf(n=4, k=3, p=win_game_prob)*win_game_prob
                    win_in_6 = BinomDist.pmf(n=5, k=3, p=win_game_prob)*win_game_prob
                    win_in_7 = BinomDist.pmf(n=6, k=3, p=win_game_prob)*win_game_prob


                    win_series = float(win_in_4) + float(win_in_5) + float(win_in_6) + float(win_in_7)
                    ws_overall_prob = matchup_prob*win_series

                    ws_prob += ws_overall_prob

                overall_prob = ws_prob
                ws_dict[team_name] = [overall_prob, 1.0, False]

            col_name = 'make_ws'
            adjust_probabilities(ws_dict, col_name, 1.0, _type)

def process_champion():
    print "win world series"
    
    for _type in ('roster', 'projected'):
        # print '\t', _type
        for conf in ('AL', 'NL'):

            team_query = "SELECT team_abb, team_name, make_ws FROM __playoff_probabilities WHERE strength_type = '%s' AND LEFT(division,2) = '%s'" % (_type, conf)
            team_res = db.query(team_query)

            champ_dict = {}
            for team_row in team_res:
                team_abb, team_name, make_ws = team_row

                # print '\t\t', team_name

                oppn_qry = """SELECT team_abb, team_name, make_ws
                FROM __playoff_probabilities
                WHERE strength_type = '%s'
                AND LEFT(division,2) != '%s';"""
                oppn_query = oppn_qry % (_type, conf)

                # raw_input(oppn_query)
                oppn_res = db.query(oppn_query)

                champ_prob = 0.0
                for oppn_row in oppn_res:
                    oppn_abb, oppn_name, oppn_ws = oppn_row

                    matchup_prob = float(make_ws)*float(oppn_ws)

                    win_game_query = "SELECT odds_ratio FROM __matchup_matrix WHERE team_abb = '%s' AND opponent = '%s' AND strength_type = '%s'" % (team_abb, oppn_abb, _type)
                    win_game_prob = float(db.query(win_game_query)[0][0])

                    win_in_4 = BinomDist.pmf(n=4, k=4, p=win_game_prob)
                    win_in_5 = BinomDist.pmf(n=4, k=3, p=win_game_prob)*win_game_prob
                    win_in_6 = BinomDist.pmf(n=5, k=3, p=win_game_prob)*win_game_prob
                    win_in_7 = BinomDist.pmf(n=6, k=3, p=win_game_prob)*win_game_prob

                    win_series = float(win_in_4) + float(win_in_5) + float(win_in_6) + float(win_in_7)
                    champ_overall_prob = matchup_prob*win_series

                    champ_prob += champ_overall_prob

                overall_prob = champ_prob
                champ_dict[team_name] = [overall_prob, 1.0, False]

            col_name = 'win_ws'
            adjust_probabilities(champ_dict, col_name, 0.5, _type)

def adjust_probabilities(prob_dict, col_name, sum_to, _type):
    bool_temp = False
    final_vals = {}
    while bool_temp is False:
        bool_temp = True

        prob_sum = 0.0
        for tm, values in prob_dict.items():
            curr_prob, max_prob, tm_bool = values
            if tm_bool is False:
                prob_sum += curr_prob

        prob_factor = prob_sum/sum_to

        for tm, values in prob_dict.items():
            curr_prob, max_prob, tm_bool = values

            adj_val = curr_prob/prob_factor

            if (adj_val > max_prob and tm_bool is False):
                sum_to = sum_to - max_prob
                bool_temp = False
                prob_dict[tm] = [curr_prob, max_prob, True]
                final_vals[tm] = max_prob

            elif tm_bool is True:
                final_vals[tm] = max_prob
            else:
                prob_dict[tm] = [curr_prob, max_prob, False]
                final_vals[tm] = adj_val

    for tm, val in final_vals.items():
        db.updateRow({col_name:val},"__playoff_probabilities",("team_name","strength_type"),(tm,_type),operators=['=','='])
        db.conn.commit()

def get_probabilities(team_name, oppn_teams, strength_pct, projected_std, _type):
    prob_list = []
    prob_name_list = []
    for opponent in oppn_teams:
        oppn_entry = {}
        qry = """SELECT p.mean_W/162, p.std, ros_W+ros_L
        FROM __team_strength
        JOIN __playoff_probabilities p USING (team_abb, team_name)
        WHERE strength_type = '%s'
        AND team_name = '%s';"""
        query = qry % (_type, opponent)
        # raw_input(query)
        res = db.query(query)

        oppn_pct, oppn_std, games_left = res[0]

        if _type == 'roster':
            games_played = 0.0
            proj_std = float(projected_std)/float(162.0)
            oppn_std = float(oppn_std)/float(162.0)
        else:
            games_played = 162.0-float(games_left)
            proj_std = float(projected_std)/float(162.0)
            oppn_std = float(oppn_std)/float(162.0)

        diff_W = float(strength_pct) - float(oppn_pct)
        diff_std = math.sqrt(proj_std**2 + oppn_std**2)

        dist_prob = 1.0 - NormDist(diff_W, diff_std).cdf(0)

        oppn_entry[opponent] = dist_prob

        prob_name_list.append(oppn_entry)
        prob_list.append(dist_prob)


    return prob_list, prob_name_list


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process()
    