from py_db import db
import argparse
import math


db = db('NSBL')


def process(team_A, team_B, games_need_to_win, series_length):

    print '\n\n'

    win_game_query = "SELECT odds_ratio FROM __matchup_matrix JOIN (SELECT team_abb, MAX(year) AS year, MAX(games_played) AS games_played FROM __matchup_matrix GROUP BY team_abb) t2 USING (team_abb, year, games_played) WHERE team_abb = '%s' AND opponent = '%s' AND strength_type = '%s'" % (team_A, team_B, 'projected')

    win_pct = float(db.query(win_game_query)[0][0])

    tot = 0
    for i in range (games_need_to_win, series_length+1):

        atts = float(math.factorial(series_length)) / float(math.factorial(i) * math.factorial(series_length-i))

        prob = float( (win_pct)**i * (1-win_pct)**(series_length-i) )
        
        print 'prob of winning %s games: %s, (%s)' %(str(i), str(atts*prob*100)+'%', str(atts*prob*win_pct*100)+'%')

        sum_val = atts*prob

        tot += sum_val

    statement = "Probability of %s winning at least %s of %s games against %s:" % (team_A, str(games_need_to_win), str(series_length), team_B)

    statement_2 = "(based on single game win expectancy of %s @ %s)" % (team_A, str(win_pct*100)+'%')

    statement_3 = "(probability of %s winning - %s)" % (team_B, str((1-tot)*100)+'%')

    print '\n', statement
    print '\t', statement_2
    print '\t\t', str(tot*100)+'%'
    print '\t\t', statement_3
    print '\n\n\n'


if __name__ == "__main__":  

    parser = argparse.ArgumentParser()
    parser.add_argument('--team_A',default='TAM')
    parser.add_argument('--team_B',default='WAS')
    parser.add_argument('--games_need_to_win',default=2)
    parser.add_argument('--series_length',default=2)

    args = parser.parse_args()

    process(args.team_A, args.team_B, args.games_need_to_win, args.series_length)

