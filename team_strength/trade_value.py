from py_db import db
import NSBL_helpers as helper
import argparse
from time import time



# script that estimates trade values for the ~1750 players on NSBL rosters
# it first looks for zips projections/age for a player; if those do not exists it looks for the player in the proespect database
# if neither exist, the player's trade value is null
# otherwise, it uses zips projections of prospect FV values to determine value over the length of their contract, and compares to how much the player is being paid


db = db('NSBL')

# year: [years_remaining, salary multiplied, reverse index, ceiling, floor]
# select year, max(salary), min(salary) from current_rosters_excel where year not in ('v', 'ce', 'mli') group by year
years_map = {'6th':[1, 0.8, 5, 17.500, 2.00], '5th':[2, .6, 4, 9, 1.50], '4th':[3, .4, 3, 5.5, 1.0], '3rd':[4, 0.2, 2, 2.5, 0.650], '2nd':[5, 0.1, 1, 1.250, 0.600], '1st':[6, 1, 0, 0.550, 0.550], 'XXX':[6, 1, -1, 0.550, 0.550]}


def process(year):
    start_time = time()

    player_values(year)

    team_values(year)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "trade_value.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def player_values(year):
    clear_current = db.query("DELETE FROM _trade_value WHERE year = %s" % (year))
    db.conn.commit()

    season_gp = db.query("SELECT gs FROM processed_league_averages_pitching WHERE year = %s" % (year))
    if season_gp == ():
        season_gp = 0
    else:
        season_gp = float(season_gp[0][0])

    season_pct_multiplier = float(1-(season_gp/(30*162)))

    # print season_pct_multiplier


    qry = """
    SELECT r.*
        , COALESCE(p.age, zh.age, zp.age) AS age
        , COALESCE(p.FG_Team, p.MLB_Team) AS p_Team
        , p.adj_FV
        , IF(r.position != 'p', zh.team_abb, zp.team_abb) AS z_Team
        , IF(r.position != 'p', zh.PA, zp.TBF) AS z_PA
        , IF(r.position != 'p', zh.WAR, zp.WAR) AS zWAR
        FROM NSBL.current_rosters_excel r
        LEFT JOIN mlb_prospects._master_current p ON (1
            AND IF(r.position = 'p'
                , p.position LIKE "%%p%%"
                , p.position LIKE "%%b%%" 
                    OR p.position LIKE "%%c%%"
                    OR p.position LIKE "%%dh%%"
                    OR p.position LIKE "%%f%%"
                    OR p.position LIKE "%%ss%%"
            )
            AND find_in_set(replace(r.fname, ".", ""), replace(p.fnames, ".", "")) >= 1
            AND find_in_set(replace(r.lname, ".", ""), replace(p.lnames, ".", "")) >= 1
        )
        LEFT JOIN (
            SELECT zr.player_name
            , zfg.*
            , zr.age
            FROM NSBL.zips_fangraphs_batters_rate zfg
            JOIN(
                SELECT player
                , MAX(post_date) AS post_date
                FROM NSBL.zips_fangraphs_batters_rate
                WHERE 1
                    AND year = %s
                GROUP BY player
            ) pd USING (player, post_date)
            LEFT JOIN NSBL.zips_offense zr ON (zfg.year = zr.year
                AND replace(zfg.Player, "!", "") = replace(replace(replace(zr.player_name, "'", ""), " Acuna", " Acua"), "Kike ", "Kik ")
            )
        ) zh ON (1
            AND r.position != 'p'
            AND (replace(replace(zh.player, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.fname, ".", ""), "-", " "), "%%") OR replace(replace(zh.player_name, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.fname, ".", ""), "-", " "), "%%"))
            AND (replace(replace(zh.player, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.lname, ".", ""), "-", " "), "%%") OR replace(replace(zh.player_name, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.lname, ".", ""), "-", " "), "%%"))
        )
        LEFT JOIN (
            SELECT zr.player_name
            , zfg.*
            , zr.age
            FROM NSBL.zips_fangraphs_pitchers_rate zfg
            JOIN(
                SELECT player
                , MAX(post_date) AS post_date
                FROM NSBL.zips_fangraphs_pitchers_rate
                WHERE 1
                    AND year = %s
                GROUP BY player
            ) pd USING (player, post_date)
            LEFT JOIN NSBL.zips_pitching zr  ON (zfg.year = zr.year
                AND replace(zfg.Player, "!", "") = replace(replace(replace(zr.player_name, "'", ""), " Acuna", " Acua"), "Kike ", "Kik ")
            )
        ) zp ON (1
            AND r.position = 'p'
            AND (replace(replace(zp.player, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.fname, ".", ""), "-", " "), "%%") OR replace(replace(zp.player_name, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.fname, ".", ""), "-", " "), "%%"))
            AND (replace(replace(zp.player, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.lname, ".", ""), "-", " "), "%%") OR replace(replace(zp.player_name, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.lname, ".", ""), "-", " "), "%%"))
        )
    ;"""
    query = qry % (year, year)

    print 'querying...'
    res = db.query(query)

    for row in res:
        entry = {}
        player_name, fname, lname, team_abb, position, salary, contract_year, expires, opt, NTC, salary_counted, age, p_Team, adj_FV, z_Team, z_PA, zWAR = row

        print '\n\n', player_name, team_abb, position, salary, contract_year, expires, opt, age

        entry = {'year':year, 'player_name': player_name, 'fname': fname, 'lname': lname, 'team_abb': team_abb, 'position': position, 'salary': salary, 'contract_year': contract_year, 'expires': expires, 'opt': opt, 'NTC': NTC, 'salary_counted': salary_counted, 'curr_season_remaining':season_pct_multiplier, 'age':age, 'adj_FV':adj_FV, 'zWAR':zWAR}

        if adj_FV is not None:
            rl_team = p_Team
        elif zWAR is not None:
            rl_team = z_Team
        else:
            rl_team = None

        entry['rl_team'] = rl_team

        if expires == 0:
            years_remaining = years_map.get(contract_year)[0]
        else:
            years_remaining = expires-(year-1)
            # treat options as an extra year of value
            if opt == 'Y':
                years_remaining += 1

        
        if salary_counted == 'Y':
            entry['years_remaining'] = years_remaining - (1-season_pct_multiplier)
        else:
            entry['years_remaining'] = years_remaining

        entry['playoff_years_remaining'] = years_remaining

        if age is None:
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, playoff_war_val, playoff_dollar_val, playoff_total_salary, playoff_raw_surplus, playoff_present_surplus = None, None, None, None, None, None, None, None, None, None

        else:
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, playoff_war_val, playoff_dollar_val, playoff_total_salary, playoff_raw_surplus, playoff_present_surplus = get_war_val(year, adj_FV, age, position, zWAR, years_remaining, salary, contract_year, expires, opt, salary_counted, season_pct_multiplier)

        entry['est_war_remaining'] = war_val
        entry['est_value'] = dollar_val
        entry['est_salary'] = est_total_salary
        entry['est_raw_surplus'] = est_raw_surplus
        entry['est_net_present_value'] = est_present_surplus

        entry['playoff_war_remaining'] = playoff_war_val
        entry['playoff_value'] = playoff_dollar_val
        entry['playoff_salary'] = playoff_total_salary
        entry['playoff_raw_surplus'] = playoff_raw_surplus
        entry['playoff_net_present_value'] = playoff_present_surplus

        # for k,v in entry.items():
        #     print k, v
        print entry

        db.insertRowDict(entry, '_trade_value', insertMany=False, replace=True, rid=0, debug=1)
        db.conn.commit()

def get_war_val(year, adj_FV, age, position, zWAR, years_remaining, salary, contract_year, expires, opt, salary_counted, season_pct_multiplier):
    salary = float(salary)
    if zWAR is not None:
        zWAR = float(zWAR)

    def age_curve(current_age, position, current_war, years_remaining, salary, salary_counted, season_pct_multiplier, contract='Vet'):
        # curve value is a decay function with "peak" age (age_multiplier = 1) at 26 for hitters and 25 for pitchers. The pitcher curve is steeper
        # dollar_value: 6 mil/WAR in 2018, increases by 0.4 mil/WAR each year
        current_age = round(float(current_age),0)
        age_multiplier = 1
        war_val = 0
        dollar_val = 0
        est_total_salary = 0
        est_raw_surplus = 0
        est_present_surplus = 0

        playoff_war_val = 0
        playoff_dollar_val = 0
        playoff_total_salary = 0
        playoff_raw_surplus = 0
        playoff_present_surplus = 0

        for yr in range (0, years_remaining):
            proj_age = current_age + yr

            if yr == 0:
                age_multiplier = 1
            elif position == 'p':
                age_multiplier *= (1-((0.97**(proj_age))*(proj_age-25))/8)
            else:
                age_multiplier *= (1-((0.95**(proj_age))*(proj_age-26))/10)

            year_war = min(max(current_war,0)*age_multiplier, 10)
            dollar_multiplier = (7.5 + yr*0.4) 
            year_dollar = year_war * dollar_multiplier

            if contract != 'Vet':
                for k, v in years_map.items():
                    val_multiplier, indx, ceiling, floor = v[1], v[0], v[3], v[4]
                    if yr == 0:
                        est_year_salary = salary
                    elif years_remaining-yr == indx:
                        est_year_salary = min(max(val_multiplier * year_dollar, floor), ceiling)
                    est_year_surplus = max(year_dollar - est_year_salary, 0)
            else:
                est_year_salary = salary
                est_year_surplus = year_dollar - est_year_salary

            playoff_war_val += year_war
            playoff_dollar_val += year_dollar
            playoff_total_salary += est_year_salary
            playoff_raw_surplus += est_year_surplus

            playoff_present_surplus += est_year_surplus*(0.92**yr)

            if yr == 0 and salary_counted == 'Y':
                year_war = year_war*season_pct_multiplier
                est_year_salary = est_year_salary*season_pct_multiplier
                est_year_surplus = est_year_surplus*season_pct_multiplier
                year_dollar = year_dollar*season_pct_multiplier

            war_val += year_war
            dollar_val += year_dollar
            est_total_salary += est_year_salary
            est_raw_surplus += est_year_surplus

            # 8% discount rate (0.92^n)
            est_year_present_surplus = est_year_surplus*(0.92**yr)
            est_present_surplus += est_year_present_surplus


            print '\t', year+yr, ': ', current_age, current_war, '|||', round(proj_age, 1), round(year_war, 1), round(age_multiplier, 2), '|||', round(year_dollar, 3), round(dollar_multiplier, 3), '|||', round(est_year_salary, 3), round(est_year_surplus, 3), round(est_year_present_surplus, 3), season_pct_multiplier

        # print war_val
        return war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, playoff_war_val, playoff_dollar_val, playoff_total_salary, playoff_raw_surplus, playoff_present_surplus


    if contract_year not in ('V', 'CE', 'MLI'):
        contract = 'NonVet'
    else:
        contract = 'Vet'

    if adj_FV is not None:
        adj_FV = float(adj_FV)
        age = float(age)
        if position != 'p':
            if adj_FV <= 35:
                war_val = 0.1
            elif adj_FV > 35 and adj_FV <= 50:
                war_val = 0.1 + (adj_FV-35)*0.15
            elif adj_FV > 50:
                war_val = 2.35 + (adj_FV-50)*0.5
        else:
            if adj_FV <= 35:
                war_val = 0.1
            elif adj_FV > 35 and adj_FV <= 50:
                war_val = 0.1 + (adj_FV-35)*0.15
            elif adj_FV > 50:
                war_val = 2.35 + (adj_FV-50)*0.35
        year_war_avg = (war_val) / (years_remaining)
        playoff_war_val = war_val
        # print '\n', entry, adj_FV, war_val, '\n'

        if contract_year not in ('V', 'CE', 'MLI'):
            year_dollar = (7.5 + (year-2019)*0.4) * year_war_avg

            war_val = 0
            dollar_val = 0
            est_total_salary = 0
            est_raw_surplus = 0

            playoff_war_val = 0
            playoff_total_salary = 0

            for yr_indx in range (6-years_remaining, 6):
                for k, v in years_map.items():
                    val_multiplier, indx, ceiling, floor = v[1], v[2], v[3], v[4]

                    if yr_indx == indx:
                        year_war = year_war_avg
                        est_year_salary = min(min(max(val_multiplier * year_dollar, floor), ceiling), year_dollar)

                        playoff_war_val += year_war
                        playoff_total_salary += est_year_salary

                        if yr_indx == 6-years_remaining and salary_counted == 'Y':
                            year_war = year_war_avg*season_pct_multiplier
                            est_year_salary = est_year_salary*season_pct_multiplier


                        print year_war, est_year_salary, year_dollar, season_pct_multiplier
                        war_val += year_war
                        est_total_salary += est_year_salary
                        # print yr_indx, year_dollar, val_multiplier, est_year_salary

        else:
            est_total_salary = salary*years_remaining
            playoff_total_salary = est_total_salary

        # for zips players, we have an estimate for $/war each season, but for prospects, we treat it as a lump sum (since we don't know how their projected war will be dispersed) (7.5 is the current $/WAR, and 0.4 is the inflation multiplier for future season)
        dollar_val = (7.5 + (year-2019)*0.4) * war_val
        playoff_dollar_val = (7.5 + (year-2019)*0.4) * playoff_war_val
        
        playoff_raw_surplus = playoff_dollar_val - playoff_total_salary
        playoff_present_surplus = playoff_raw_surplus

        est_raw_surplus = dollar_val - est_total_salary
        est_present_surplus = est_raw_surplus

        if zWAR is not None:
            temp_war_val, temp_dollar_val, temp_est_total_salary, temp_est_raw_surplus, temp_est_present_surplus, temp_playoff_war_val, temp_playoff_dollar_val, temp_playoff_total_salary, temp_playoff_raw_surplus, temp_playoff_present_surplus = age_curve(age, position, zWAR, years_remaining, salary, salary_counted, season_pct_multiplier, contract)

            if temp_war_val > war_val:
                war_val = temp_war_val
                dollar_val = temp_dollar_val
                est_total_salary = temp_est_total_salary
                est_raw_surplus = temp_est_raw_surplus
                est_present_surplus = temp_est_present_surplus

            if temp_playoff_war_val > playoff_war_val:
                playoff_war_val = temp_playoff_war_val
                playoff_dollar_val = temp_playoff_dollar_val
                playoff_total_salary = temp_playoff_total_salary
                playoff_raw_surplus = temp_playoff_raw_surplus
                playoff_present_surplus = temp_playoff_present_surplus

    else:
        war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, playoff_war_val, playoff_dollar_val, playoff_total_salary, playoff_raw_surplus, playoff_present_surplus = age_curve(age, position, zWAR, years_remaining, salary, salary_counted, season_pct_multiplier, contract)

    return war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, playoff_war_val, playoff_dollar_val, playoff_total_salary, playoff_raw_surplus, playoff_present_surplus


def team_values(year):
    season_gp = db.query("SELECT gs FROM processed_league_averages_pitching WHERE year = %s" % (year))
    if season_gp == ():
        season_gp = 0
    else:
        season_gp = float(season_gp[0][0])

    season_string = str(int(season_gp/2)) + " of " + str(30*81)

    qry = """SET SESSION group_concat_max_len = 1000000;
    DROP TABLE IF EXISTS _trade_value_teams;
    CREATE TABLE _trade_value_teams AS
    SELECT year
    , '%s' as completed
    , team_abb

    , COUNT(*) AS roster_size
    , SUM(IF(est_value IS NOT NULL, 1, 0)) AS valued_players
    , SUM(IF(adj_FV IS NOT NULL, 1, 0)) AS prospects

    , SUM(IF(adj_FV IS NULL AND zWAR IS NOT NULL, 1, 0)) AS MLB_players
    , SUM(IF(est_value IS NULL, 1, 0)) AS missing_players

    , SUM(est_war_remaining) AS total_war
    , SUM(est_value) AS total_value
    , SUM(est_salary) AS total_salary
    , SUM(est_raw_surplus) AS total_raw_surplus
    , SUM(est_net_present_value) AS total_net_present_value

    , SUM(IF(adj_FV IS NOT NULL, est_war_remaining, 0)) AS prospect_war
    , SUM(IF(adj_FV IS NOT NULL, est_value, 0)) AS prospect_value
    , SUM(IF(adj_FV IS NOT NULL, est_salary, 0)) AS prospect_salary
    , SUM(IF(adj_FV IS NOT NULL, est_raw_surplus, 0)) AS prospect_raw_surplus
    , SUM(IF(adj_FV IS NOT NULL, est_net_present_value, 0)) AS prospect_net_present_value

    , SUM(IF(adj_FV IS NULL AND zWAR IS NOT NULL, est_war_remaining, 0)) AS MLB_player_war
    , SUM(IF(adj_FV IS NULL AND zWAR IS NOT NULL, est_value, 0)) AS MLB_player_value
    , SUM(IF(adj_FV IS NULL AND zWAR IS NOT NULL, est_salary, 0)) AS MLB_player_salary
    , SUM(IF(adj_FV IS NULL AND zWAR IS NOT NULL, est_raw_surplus, 0)) AS MLB_player_raw_surplus
    , SUM(IF(adj_FV IS NULL AND zWAR IS NOT NULL, est_net_present_value, 0)) AS MLB_player_net_present_value

    , SUM(playoff_war_remaining) AS playoff_war
    , SUM(playoff_value) AS playoff_value
    , SUM(playoff_salary) AS playoff_salary
    , SUM(playoff_raw_surplus) AS playoff_raw_surplus
    , SUM(playoff_net_present_value) AS playoff_net_present_value

    , GROUP_CONCAT(DISTINCT CONCAT(
        player_name
        , ' ($', ifnull(est_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, ' zWAR'))
        , ')'
        ) ORDER BY est_net_present_value DESC SEPARATOR '\n'
    ) AS all_player_values

    , GROUP_CONCAT(DISTINCT CONCAT(
        player_name
        , ' ($', ifnull(playoff_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, ' zWAR'))
        , ')'
        ) ORDER BY est_net_present_value DESC SEPARATOR '\n'
    ) AS all_player_playoff_values

    , GROUP_CONCAT(IF(adj_FV IS NOT NULL, CONCAT(
        player_name
        , ' ($', ifnull(est_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, ' zWAR'))
        , ')'
        ), NULL) ORDER BY est_net_present_value DESC SEPARATOR '\n'
    ) AS prospect_values

    , GROUP_CONCAT(IF(adj_FV IS NULL AND zWAR IS NOT NULL, CONCAT(
        player_name
        , ' ($', ifnull(est_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, ' zWAR'))
        , ')'
        ), NULL) ORDER BY est_net_present_value DESC SEPARATOR '\n'
    ) AS MLB_player_values

    , GROUP_CONCAT(IF(est_value IS NULL, CONCAT(
        player_name
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, ' zWAR'))
        , ')'
        ), NULL) SEPARATOR '\n'
    ) AS missing_player_values

    FROM _trade_value
    WHERE 1
        AND year = %s
    GROUP BY year, team_abb
    ;"""

    query = qry % (season_string, year)

    for q in query.split(';')[:-1]:
        # raw_input(q)
        db.query(q)
        db.conn.commit()


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2019)
    args = parser.parse_args()
    
    process(args.year)
    

