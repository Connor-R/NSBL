from py_db import db
import argparse
from decimal import Decimal

db = db('NSBL')

# Needs to be run every week after the registers are created
# Only works on years >= 2017
# Takes players who play for multiple teams in a season and splits their statistics into multiple entries (1 for each team they played on, as well as one for their full season)
# register_primary has more players than other registers because it splits multi-team entries 


def process(year):
    if year < 2017:
        pass
    else:
        multi_hitters(year)
        multi_pitchers(year)



def get_current_team(player_name, position, age):
    if player_name[len(player_name)-1:] in ("*", '#'):
        search_name = player_name[:len(player_name)-1]
    else:
        search_name = player_name

    curr_team_q = """SELECT
team_abb
FROM current_rosters
JOIN teams USING (team_id, year)
WHERE player_name = '%s'
AND position = '%s'
AND age = %s
"""
    curr_team_qry = curr_team_q % (search_name, position, age)

    curr_team_query = db.query(curr_team_qry)
    if curr_team_qry != ():
        curr_team = curr_team_query[0][0]
    else:
        curr_team = ''

    return curr_team


def multi_hitters(year):
    entries = []

    players_list_q = """SELECT
year,
player_name
FROM
register_batting_primary
WHERE year = %s
AND team_abb = ''
"""
    player_list_qry = players_list_q % year

    players_list = db.query(player_list_qry)

    for row in players_list:
        year, player_name = row

        totals_q = """SELECT
player_name,
position,
age,
pa,
ab,
(h-2b-3b-hr) as 1b, 2b, 3b, hr, r, rbi, bb, k, hbp, sb, cs
FROM register_batting_primary
JOIN register_batting_secondary USING (year, player_name, team_abb, position, age)
JOIN register_batting_analytical USING (year, player_name, team_abb, position, age)
WHERE year = %s
AND player_name = '%s'
AND team_abb = '';
"""
        totals_qry = totals_q % (year, player_name)

        totals_query = db.query(totals_qry)

        if totals_query != ():
            totals = totals_query[0]
        
            player_name, position, age, tot_pa, tot_ab, tot_1b, tot_2b, tot_3b, tot_hr, tot_r, tot_rbi, tot_bb, tot_k, tot_hbp, tot_sb, tot_cs = totals  

            curr_team = get_current_team(player_name, position, age)

            entry = {}
            entry['year'] = year
            entry['team_abb'] = curr_team
            entry['player_name'] = player_name
            entry['position'] = position
            entry['age'] = age

            prev_teams_q = """SELECT
position,
age,
SUM(pa),
SUM(ab),
(SUM(h)-SUM(2b)-SUM(3b)-SUM(hr)) as 1b, SUM(2b), SUM(3b), SUM(hr), SUM(r), SUM(rbi), SUM(bb), SUM(k), SUM(hbp), SUM(sb), SUM(cs)
FROM register_batting_primary
JOIN register_batting_secondary USING (year, player_name, team_abb, position, age)
JOIN register_batting_analytical USING (year, player_name, team_abb, position, age)
WHERE year = %s
AND player_name = '%s'
AND team_abb not in ('', '%s');
"""
            prev_teams_qry = prev_teams_q % (year, player_name, curr_team)

            prev_teams_query = db.query(prev_teams_qry) 

            if prev_teams_query == ((None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),):

                prev_teams = ['','',0,0,0,0,0,0,0,0,0,0,0,0,0]

            elif prev_teams_query != ():
                prev_teams = prev_teams_query[0]

            prev_pos, prev_age, prev_pa, prev_ab, prev_1b, prev_2b, prev_3b, prev_hr, prev_r, prev_rbi, prev_bb, prev_k, prev_hbp, prev_sb, prev_cs = prev_teams


            curr_pa = tot_pa - prev_pa
            curr_1b = tot_1b - prev_1b
            curr_2b = tot_2b - prev_2b
            curr_3b = tot_3b - prev_3b
            curr_hr = tot_hr - prev_hr
            curr_r = tot_r - prev_r
            curr_rbi = tot_rbi - prev_rbi
            curr_bb = tot_bb - prev_bb
            curr_k = tot_k - prev_k
            curr_hbp = tot_hbp - prev_hbp
            curr_sb = tot_sb - prev_sb
            curr_cs = tot_cs - prev_cs
            curr_ab = tot_ab - prev_ab

            curr_h = curr_1b + curr_2b + curr_3b + curr_hr

            avg = (float(curr_h)/float(curr_ab))
            obp = (float(curr_h)+float(curr_bb)+float(curr_hbp))/float(curr_pa)
            slg = (float(curr_1b)+2*float(curr_2b)+3*float(curr_3b)+4*float(curr_hr))/float(curr_ab)

            entry['avg'] = avg
            entry['obp'] = obp
            entry['slg'] = slg
            entry['ab'] = curr_ab
            entry['h'] = curr_h
            entry['2b'] = curr_2b
            entry['3b'] = curr_3b
            entry['hr'] = curr_hr
            entry['r'] = curr_r
            entry['rbi'] = curr_rbi
            entry['hbp'] = curr_hbp
            entry['bb'] = curr_bb
            entry['k'] = curr_k
            entry['sb'] = curr_sb
            entry['cs'] = curr_cs

            entries.append(entry)

    if entries != []: 
        db.insertRowDict(entries, 'register_batting_primary', replace=True, insertMany=True, rid=0)
    db.conn.commit()


def multi_pitchers(year):
    entries = []

    players_list_q = """SELECT
year,
player_name
FROM
register_pitching_primary
WHERE year = %s
AND team_abb = ''
"""
    player_list_qry = players_list_q % year

    players_list = db.query(player_list_qry)

    for row in players_list:
        year, player_name = row

        totals_q = """SELECT
player_name,
position,
age,
w, l, sv, g, gs, cg, sho,
SUM(ROUND(ip) + (10 * (ip - ROUND(ip)) / 3)) AS ip,
h, r, er, bb, k, hr, gdp
FROM register_pitching_primary
WHERE year = %s
AND player_name = '%s'
AND team_abb = '';
"""
        totals_qry = totals_q % (year, player_name)

        totals_query = db.query(totals_qry)

        if totals_query != ():
            totals = totals_query[0]
        
            player_name, position, age, tot_w, tot_l, tot_sv, tot_g, tot_gs, tot_cg, tot_sho, tot_ip, tot_h, tot_r, tot_er, tot_bb, tot_k, tot_hr, tot_gdp = totals  

            curr_team = get_current_team(player_name, position, age)

            entry = {}
            entry['year'] = year
            entry['team_abb'] = curr_team
            entry['player_name'] = player_name
            entry['position'] = position
            entry['age'] = age

            prev_teams_q = """SELECT
player_name,
position,
age,
w, l, sv, g, gs, cg, sho,
SUM(ROUND(ip) + (10 * (ip - ROUND(ip)) / 3)) AS ip,
h, r, er, bb, k, hr, gdp
FROM register_pitching_primary
WHERE year = %s
AND player_name = '%s'
AND team_abb not in ('', '%s');
"""
            prev_teams_qry = prev_teams_q % (year, player_name, curr_team)

            prev_teams_query = db.query(prev_teams_qry) 

            if prev_teams_query == ((None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),):

                prev_teams = ['','','',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

            elif prev_teams_query != ():
                prev_teams = prev_teams_query[0]

            prev_name, prev_pos, prev_age, prev_w, prev_l, prev_sv, prev_g, prev_gs, prev_cg, prev_sho, prev_ip, prev_h, prev_r, prev_er, prev_bb, prev_k, prev_hr, prev_gdp = prev_teams


            curr_w = tot_w - prev_w
            curr_l = tot_l - prev_l
            curr_sv = tot_sv - prev_sv
            curr_g = tot_g - prev_g
            curr_gs = tot_gs - prev_gs
            curr_cg = tot_cg - prev_cg
            curr_sho = tot_sho - prev_sho
            curr_ip = tot_ip - prev_ip
            curr_h = tot_h - prev_h
            curr_r = tot_r - prev_r
            curr_er = tot_er - prev_er
            curr_bb = tot_bb - prev_bb
            curr_k = tot_k - prev_k
            curr_hr = tot_hr - prev_hr
            curr_gdp = tot_gdp - prev_gdp


            curr_era = 9*(float(curr_er)/float(curr_ip))

            entry['era'] = curr_era
            entry['w'] = curr_w
            entry['l'] = curr_l
            entry['sv'] = curr_sv
            entry['g'] = curr_g
            entry['gs'] = curr_gs
            entry['cg'] = curr_cg
            entry['sho'] = curr_sho
            entry['ip'] = curr_ip
            entry['h'] = curr_h
            entry['r'] = curr_r
            entry['er'] = curr_er
            entry['bb'] = curr_bb
            entry['k'] = curr_k
            entry['hr'] = curr_hr
            entry['gdp'] = curr_gdp

            entries.append(entry)


    if entries != []: 
        db.insertRowDict(entries, 'register_pitching_primary', replace=True, insertMany=True, rid=0)
    db.conn.commit()

    # # used for debugging
    # for e in entries:
    #     print e
    #     raw_input("")
    

if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process(args.year)