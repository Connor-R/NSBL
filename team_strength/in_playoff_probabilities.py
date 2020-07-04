from py_db import db
from decimal import Decimal
import NSBL_helpers as helper
from datetime import datetime
from time import time
import numpy as np
import argparse
import math
from scipy.stats import norm as NormDist, binom as BinomDist


# script that produces in-playoffs probability charts


db = db('NSBL')


def process(year):

    start_time = time()

    timestamp = datetime.now()

    populate_bracket(year, timestamp)
    current_series(year, timestamp)
    get_playoff_teams(year, timestamp)

    process_wc(year, timestamp)
    process_ds(year, timestamp)
    process_cs(year, timestamp)
    process_ws(year, timestamp)
    process_champion(year, timestamp)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "in_playoff_probabilities.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def populate_bracket(year, timestamp):
    print '\tpopulating __in_playoff_bracket'

    games_query = "SELECT IFNULL(SUM(IF(winning_team IS NOT NULL,1,0)),0) FROM __in_playoff_game_results WHERE year = %s;" % (year)

    total_playoff_games_played = db.query(games_query)[0][0]

    for lg in ('AL', 'NL', ''):
        for series in ('WC', 'DS1', 'DS2', 'CS', 'WS'):
            series_id = lg+series

            qry = """SELECT teamA, teamB, 
            SUM(IF(winning_team=teamA,1,0)) as teamA_wins,
            SUM(IF(winning_team=teamB,1,0)) as teamB_wins
            FROM __in_playoff_game_results
            WHERE series_id = '%s'
            AND year = %s;"""

            query = qry % (series_id, year)

            res = db.query(query)

            if res[0][0] is not None:
                teamA, teamB, teamA_wins, teamB_wins = res[0]

                for strength_type in ('roster', 'projected'):

                    entries = []
                    for tm in (teamA, teamB):
                        entry = {'update_time':timestamp, 'series_id':series_id, 'year':year,'strength_type':strength_type, 'total_playoff_games_played':total_playoff_games_played}
                        if tm == teamA:
                            entry['team'] = teamA
                            entry['opponent'] = teamB
                            entry['series_wins'] = teamA_wins
                            entry['series_losses'] = teamB_wins

                        elif tm == teamB:
                            entry['team'] = teamB
                            entry['opponent'] = teamA
                            entry['series_wins'] = teamB_wins
                            entry['series_losses'] = teamA_wins   
                        
                        entries.append(entry)

                    db.insertRowDict(entries, '__in_playoff_bracket', insertMany=True, replace=True, rid=0,debug=1)
                    db.conn.commit()

def current_series(year, timestamp):
    print '\tdetermining current series probabilities'

    games_query = "SELECT IFNULL(SUM(IF(winning_team IS NOT NULL,1,0)),0) FROM __in_playoff_game_results WHERE year = %s;" % (year)

    total_playoff_games_played = db.query(games_query)[0][0]

    qry = """SELECT 
    series_id, year, strength_type, 
    team, opponent,
    series_wins, series_losses
    FROM __in_playoff_bracket
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_bracket)
    AND year = %s;"""

    query = qry % (year)

    res = db.query(query)

    for row in res:
        series_id, year, strength_type, team, opponent, series_wins, series_losses = row

        series_type = series_id.replace('AL','').replace('NL','')[:2]
        games_dict = {'WC':1, 'DS':5, 'CS':7, 'WS':7}
        series_games = games_dict.get(series_type)

        team_abb = helper.get_team_abb(team, year)
        oppn_abb = helper.get_team_abb(opponent, year)

        team_winProb = get_single_game_win_prob(team_abb, oppn_abb, strength_type, year)

        entry = {'update_time':timestamp, 'series_id':series_id, 'year':year, 'team':team, 'opponent':opponent, 'series_wins':series_wins, 'series_losses':series_losses, 'strength_type':strength_type, 'team_winProb':team_winProb, 'total_playoff_games_played':total_playoff_games_played}

        team_probs = []

        if series_wins == series_games/2+1:
            team_probs.append(1)
            total_games = series_wins+series_losses
            if total_games > 2:
                colName = 'team_in'+str(total_games)
                entry[colName] = 1

        if series_losses == series_games/2+1:
            team_probs.append(0)

        if (series_wins != series_games/2+1 and series_losses != series_games/2+1):
            for end_game in range(series_games/2+1, series_games+1-series_losses):
                team_in_N = BinomDist.pmf(n=end_game-1-series_wins, k=(series_games/2-series_wins), p=team_winProb) * team_winProb

                col_name = 'team_in'+str(end_game+series_losses)

                team_probs.append(team_in_N)

                if end_game > 2:
                    entry[col_name] = team_in_N

        entry['team_seriesProb'] = sum(team_probs)

        db.insertRowDict(entry, '__in_playoff_bracket', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()


def get_playoff_teams(year, timestamp):
    print '\tgetting playoff teams'

    games_query = "SELECT IFNULL(SUM(IF(winning_team IS NOT NULL,1,0)),0) FROM __in_playoff_game_results WHERE year = %s;" % (year)

    total_playoff_games_played = db.query(games_query)[0][0]

    entries = []
    for strength_type in ('projected', 'roster'):
        qry = """SELECT 
        team_abb, team_name, division, top_seed, win_division, (wc_1+wc_2)
        FROM __playoff_probabilities
        JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
        WHERE strength_type = 'projected' 
        AND (win_division+wc_1+wc_2 = 1.000)
        AND year = %s;"""
        query = qry % (year)

        res = db.query(query)

        for row in res:
            team_abb, team_name, division, top_seed, win_division, wild_card = row

            entry = {'update_time':timestamp, 'year':year, 'team_name':team_name, 'team_abb':team_abb, 'strength_type':strength_type, 'total_playoff_games_played':total_playoff_games_played, 'division':division, 'top_seed':top_seed, 'win_division':win_division, 'wild_card':wild_card}

            strength_qry = """SELECT 
            strength_pct
            FROM __playoff_probabilities
            JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __playoff_probabilities GROUP BY team_abb, year) t2 USING (team_abb, year, games_played)
            WHERE strength_type = '%s' 
            AND team_name = '%s'
            AND year = %s;"""

            strength_query = strength_qry % (strength_type, team_name, year)

            strength_pct = db.query(strength_query)

            entry['strength_pct'] = strength_pct

            entries.append(entry)


    db.insertRowDict(entries, '__in_playoff_probabilities', insertMany=True, replace=True, rid=0,debug=1)
    db.conn.commit()


def process_wc(year, timestamp):
    print '\tdetermining wild card winners'
    teams_query = """SELECT year, team_name, team_abb, division, wild_card, total_playoff_games_played, strength_type
    FROM __in_playoff_probabilities
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities)
    AND wild_card != 0;"""

    res = db.query(teams_query)

    for row in res:
        year, team_name, team_abb, division, wild_card, total_playoff_games_played, strength_type = row

        lg = division[:2]

        oppn_qry = """SELECT team_name, team_abb, division, wild_card, total_playoff_games_played, strength_type
        FROM __in_playoff_probabilities
        WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities)
        AND wild_card != 0
        AND year = %s
        AND total_playoff_games_played = %s
        AND left(division,2) = '%s'
        AND strength_type = '%s'
        AND team_name != '%s';"""

        oppn_query = oppn_qry % (year, total_playoff_games_played, lg, strength_type, team_name)

        oppns = db.query(oppn_query)

        win_wc = []
        for oppn in oppns:
            oppn_name, oppn_abb, oppn_division, oppn_wild_card, foo, foo = oppn

            matchup_prob = 1

            series_id = '%sWC' % (lg)

            series_wins, series_losses = get_series_data(series_id, team_name, oppn_name, strength_type)
        
            team_winProb = get_single_game_win_prob(team_abb, oppn_abb, strength_type, year)

            series_games = 1

            series_prob = get_series_prob(series_games, series_wins, series_losses, team_winProb)

            win_wc.append(matchup_prob*series_prob)

        win_wc = sum(win_wc)

        db.updateRow({'win_wc':win_wc},"__in_playoff_probabilities",("team_name","year","total_playoff_games_played","strength_type"),(team_name,year,total_playoff_games_played,strength_type),operators=['=','=','=','='])
        db.conn.commit()


def process_ds(year, timestamp):
    print "\tmake division series"

    query = """SELECT year, team_name, total_playoff_games_played, strength_type, 
    win_division+IFNULL(win_wc,0)
    FROM __in_playoff_probabilities
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities);"""
    res = db.query(query)

    for row in res:
        year, team_name, total_playoff_games_played, strength_type, make_ds = row

        db.updateRow({'make_ds':make_ds},"__in_playoff_probabilities",("team_name","year","total_playoff_games_played","strength_type"),(team_name,year,total_playoff_games_played,strength_type),operators=['=','=','=','='])
        db.conn.commit()


def process_cs(year, timestamp):
    print "\tmake championship series"
    
    team_query = """SELECT team_abb, team_name, year, strength_type, total_playoff_games_played,
    division, top_seed, win_division, IFNULL(win_wc,0)
    FROM __in_playoff_probabilities
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities);"""
    # raw_input(team_query)
    team_res = db.query(team_query)

    cs_dict = {}
    for team_row in team_res:
        team_abb, team_name, year, strength_type, total_playoff_games_played, team_division, top_seed, win_div, win_wc = team_row

        win_2_3_seed = float(win_div)-float(top_seed)

        lg = team_division[:2]

        oppn_qry = """SELECT team_abb, team_name, top_seed, win_division, IFNULL(win_wc,0), 
        IF(division != '%s', win_division-top_seed, 0) as 'middle_seed'
        FROM __in_playoff_probabilities
        WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities)
        AND total_playoff_games_played = %s
        AND strength_type = '%s'
        AND LEFT(division,2) = '%s'
        AND team_name != '%s'
        AND year = %s;"""
        oppn_query = oppn_qry % (team_division, total_playoff_games_played, strength_type, lg, team_name, year)
        # raw_input(oppn_query)
        oppn_res = db.query(oppn_query)

        make_cs = []
        for oppn_row in oppn_res:
            oppn_abb, oppn_name, oppn_top, oppn_div, oppn_wc, oppn_2_3_seed = oppn_row

            # probability of top_seed * (oppn_wc | not wc)
            if (1.0-float(win_wc)) == 0:
                matchup1_prob = 0.0
            else:
                matchup1_prob = float(top_seed)*float(oppn_wc)/(1.0-float(win_wc))
 
            # probability of wc * (oppn_top_seed | not top_seed)
            if (1.0-float(top_seed)) == 0:
                matchup2_prob = 0.0
            else:
                matchup2_prob = float(win_wc)*float(oppn_top)/(1.0-float(top_seed))
 
            matchup3_prob = float(win_2_3_seed)*float(oppn_2_3_seed)
 
            matchup_prob = matchup1_prob + matchup2_prob + matchup3_prob

            series_id = '%sDS' % (lg)

            series_wins, series_losses = get_series_data(series_id, team_name, oppn_name, strength_type)
        
            team_winProb = get_single_game_win_prob(team_abb, oppn_abb, strength_type, year)

            series_games = 5

            series_prob = get_series_prob(series_games, series_wins, series_losses, team_winProb)

            make_cs.append(matchup_prob*series_prob)

        make_cs = sum(make_cs)

        db.updateRow({'make_cs':make_cs},"__in_playoff_probabilities",("team_name","year","total_playoff_games_played","strength_type"),(team_name,year,total_playoff_games_played,strength_type),operators=['=','=','=','='])
        db.conn.commit()


def process_ws(year, timestamp):
    print "\tmake world series"

    
    team_query = """SELECT team_abb, team_name, year, total_playoff_games_played, strength_type, division,
    IF(top_seed + IFNULL(win_wc,0) > 0, 1, 0) as 'top_round', 
    IF(win_division-top_seed > 0, 1, 0) as 'middle_round',
    make_cs
    FROM __in_playoff_probabilities
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities);"""

    # raw_input(team_query)
    team_res = db.query(team_query)

    ws_dict = {}
    for team_row in team_res:
        team_abb, team_name, year, total_playoff_games_played, strength_type, team_division, top_round, middle_round, make_cs = team_row

        lg = team_division[:2]

        oppn_qry = """SELECT team_abb, team_name, 
        IF(top_seed + IFNULL(win_wc,0) > 0, 1, 0) as 'top_round', 
        IF(win_division-top_seed > 0, 1, 0) as 'middle_round',
        make_cs
        FROM __in_playoff_probabilities
        WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities)
        AND total_playoff_games_played = %s
        AND strength_type = '%s'
        AND LEFT(division,2) = '%s'
        AND team_name != '%s'
        AND year = %s;"""
        oppn_query = oppn_qry % (total_playoff_games_played, strength_type, lg, team_name, year)
        # raw_input(oppn_query)
        oppn_res = db.query(oppn_query)

        make_ws = []
        for oppn_row in oppn_res:
            oppn_abb, oppn_name, oppn_top_round, oppn_middle_round, oppn_cs = oppn_row

            matchup_prob = float(make_cs)*float(oppn_cs)*(float(top_round)*float(oppn_middle_round) + float(middle_round)*float(oppn_top_round))

            series_id = '%sCS' % (lg)

            series_wins, series_losses = get_series_data(series_id, team_name, oppn_name, strength_type)
        
            team_winProb = get_single_game_win_prob(team_abb, oppn_abb, strength_type, year)

            series_games = 7

            series_prob = get_series_prob(series_games, series_wins, series_losses, team_winProb)

            make_ws.append(matchup_prob*series_prob)

        make_ws = sum(make_ws)

        db.updateRow({'make_ws':make_ws},"__in_playoff_probabilities",("team_name","year","total_playoff_games_played","strength_type"),(team_name,year,total_playoff_games_played,strength_type),operators=['=','=','=','='])
        db.conn.commit()


def process_champion(year, timestamp):
    pass
    print "\twin world series"
    

    team_query = """SELECT team_abb, team_name, year, total_playoff_games_played, strength_type, division,
    make_ws
    FROM __in_playoff_probabilities
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities);"""

    # raw_input(team_query)
    team_res = db.query(team_query)

    for team_row in team_res:
        team_abb, team_name, year, total_playoff_games_played, strength_type, team_division, make_ws = team_row

        lg = team_division[:2]

        oppn_qry = """SELECT team_abb, team_name, 
        make_ws
        FROM __in_playoff_probabilities
        WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_probabilities)
        AND total_playoff_games_played = %s
        AND strength_type = '%s'
        AND LEFT(division,2) != '%s'
        AND year = %s;"""
        oppn_query = oppn_qry % (total_playoff_games_played, strength_type, lg, year)

        # raw_input(oppn_query)
        oppn_res = db.query(oppn_query)

        win_ws = []
        for oppn_row in oppn_res:
            oppn_abb, oppn_name, oppn_ws = oppn_row

            matchup_prob = float(make_ws)*float(oppn_ws)

            series_id = 'WS'

            series_wins, series_losses = get_series_data(series_id, team_name, oppn_name, strength_type)
        
            team_winProb = get_single_game_win_prob(team_abb, oppn_abb, strength_type, year)

            series_games = 7

            series_prob = get_series_prob(series_games, series_wins, series_losses, team_winProb)

            win_ws.append(matchup_prob*series_prob)

        win_ws = sum(win_ws)

        db.updateRow({'win_ws':win_ws},"__in_playoff_probabilities",("team_name","year","total_playoff_games_played","strength_type"),(team_name,year,total_playoff_games_played,strength_type),operators=['=','=','=','='])
        db.conn.commit()




def get_series_data(series_id, team_name, oppn_name, strength_type):
    series_qry = """SELECT series_wins, series_losses
    FROM __in_playoff_bracket
    WHERE update_time = (SELECT MAX(update_time) FROM __in_playoff_bracket)
    AND series_id LIKE '%s%%'
    AND team = '%s'
    AND opponent = '%s'
    AND strength_type = '%s';"""
    series_query = series_qry % (series_id, team_name, oppn_name, strength_type)

    try:
        series_wins, series_losses = db.query(series_query)[0]
    except IndexError:
        series_wins, series_losses = [0,0]

    return series_wins, series_losses



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


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2018)
    args = parser.parse_args()
    
    process(args.year)
    
    