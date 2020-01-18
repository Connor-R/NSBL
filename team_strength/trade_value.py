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
# select year, max(salary), min(salary) from excel_rosters where year not in ('v', 'ce', 'mli') group by year
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
        season_gp = float(season_gp[0][0])/2

    season_pct_multiplier = float(1-(season_gp/(15*162)))

    # print season_pct_multiplier


    qry = """
    SELECT r.*
        , COALESCE(p.age, zh.age, zp.age) AS age
        , COALESCE(p.FG_Team, p.MLB_Team) AS p_Team
        , p.adj_FV
        , IF(r.position != 'p', zh.team_abb, zp.team_abb) AS z_Team
        , IF(r.position != 'p', zh.z_PA, CONCAT(zp.IP, '-', zp.GS, '/', zp.G)) AS z_usage
        , IF(r.position != 'p', zh.WAR, zp.WAR) AS zWAR
        , CASE
            WHEN IF(r.position != 'p', zh.z_PA, zp.IP) IS NULL
                THEN IF(r.position != 'p', zh.WAR, zp.WAR)
            WHEN r.position = 'c'
                THEN 500*(zh.WAR/zh.z_PA)
            WHEN r.position = 'p'
                THEN IF((zp.GS/zp.G >= 0.80 or zp.GS >= 20), 32*(zp.WAR/zp.GS), zp.WAR)
            WHEN r.position NOT IN ('p', 'c')
                THEN 600*(zh.WAR/zh.z_PA)
        END AS ScaledWAR
        , IF(r.position = 'p', IF((zp.GS/zp.G >= 0.80 or zp.GS >= 20), 'sp', 'rp'), r.position) AS pos2
        FROM NSBL.excel_rosters r
        JOIN (
            SELECT year
            , MAX(gp) AS gp
            FROM excel_rosters
            WHERE 1
                AND year = %s
        ) cur USING (year, gp)
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
            , zbc.age
            , COALESCE(zfg.PA, zbc.PA) AS z_PA
            FROM NSBL.zips_fangraphs_batters_rate zfg
            JOIN(
                SELECT player
                , MAX(post_date) AS post_date
                FROM NSBL.zips_fangraphs_batters_rate
                WHERE 1
                    AND year = %s
                GROUP BY player
            ) pd USING (player, post_date)
            JOIN NSBL.zips_fangraphs_batters_counting zbc USING (player, post_date)
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
            , zfc.age
            , zfc.IP
            , zfc.GS
            , zfc.G
            , COALESCE(zfg.FIP, zfc.FIP) AS z_FIP
            FROM NSBL.zips_fangraphs_pitchers_rate zfg
            JOIN(
                SELECT player
                , MAX(post_date) AS post_date
                FROM NSBL.zips_fangraphs_pitchers_rate
                WHERE 1
                    AND year = %s
                GROUP BY player
            ) pd USING (player, post_date)
            JOIN NSBL.zips_fangraphs_pitchers_counting zfc USING (player, post_date)
            LEFT JOIN NSBL.zips_pitching zr  ON (zfg.year = zr.year
                AND replace(zfg.Player, "!", "") = replace(replace(replace(zr.player_name, "'", ""), " Acuna", " Acua"), "Kike ", "Kik ")
            )
        ) zp ON (1
            AND r.position = 'p'
            AND (replace(replace(zp.player, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.fname, ".", ""), "-", " "), "%%") OR replace(replace(zp.player_name, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.fname, ".", ""), "-", " "), "%%"))
            AND (replace(replace(zp.player, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.lname, ".", ""), "-", " "), "%%") OR replace(replace(zp.player_name, ".", ""), "-", " ") LIKE CONCAT("%%", replace(replace(r.lname, ".", ""), "-", " "), "%%"))
        )
    ;"""
    query = qry % (year, year, year)

    print 'querying...'
    res = db.query(query)

    for row in res:
        entry = {}
        yr, gp, player_name, fname, lname, team_abb, dummy_pos, salary, contract_year, expires, opt, NTC, salary_counted, age, p_Team, adj_FV, z_Team, z_usage, zWAR, scaledWAR, position = row

        print '\n\n', player_name, team_abb, position, salary, contract_year, expires, opt, age

        entry = {'year':year, 'player_name': player_name, 'fname': fname, 'lname': lname, 'team_abb': team_abb, 'position': position, 'salary': salary, 'contract_year': contract_year, 'expires': expires, 'opt': opt, 'NTC': NTC, 'salary_counted': salary_counted, 'season_gp':season_gp, 'age':age, 'adj_FV':adj_FV, 'zWAR':zWAR, 'scaledWAR': scaledWAR}

        if adj_FV is not None:
            rl_team = p_Team
        elif zWAR is not None:
            rl_team = z_Team
        else:
            rl_team = None

        print zWAR, scaledWAR,
        if zWAR is not None:
            model_war = (float(zWAR) + float(scaledWAR))/2
        else:
            model_war = None
        print model_war

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

        entry['preseason_years_remaining'] = years_remaining

        if age is None:
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus = None, None, None, None, None, None, None, None, None, None

        else:
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus = get_war_val(year, adj_FV, age, position, model_war, years_remaining, salary, contract_year, expires, opt, salary_counted, season_pct_multiplier)

        entry['est_war_remaining'] = war_val
        entry['est_value'] = dollar_val
        entry['est_salary'] = est_total_salary
        entry['est_raw_surplus'] = est_raw_surplus
        entry['est_net_present_value'] = est_present_surplus

        entry['preseason_war_remaining'] = preseason_war_val
        entry['preseason_value'] = preseason_dollar_val
        entry['preseason_salary'] = preseason_total_salary
        entry['preseason_raw_surplus'] = preseason_raw_surplus
        entry['preseason_net_present_value'] = preseason_present_surplus

        # for k,v in entry.items():
        #     print k, v
        print entry

        db.insertRowDict(entry, '_trade_value', insertMany=False, replace=True, rid=0, debug=1)
        db.conn.commit()

def get_war_val(year, adj_FV, age, position, model_war, years_remaining, salary, contract_year, expires, opt, salary_counted, season_pct_multiplier):
    salary = float(salary)
    if model_war is not None:
        model_war = float(model_war)

    def age_curve(current_age, position, current_war, years_remaining, salary, salary_counted, season_pct_multiplier, contract='Vet'):
        # curve value is a decay function with "peak" age (age_multiplier = 1) at 26 for hitters and 25 for pitchers. The pitcher curve is steeper
        # dollar_value:
            # rps between 0 and 0.5 WAR: 4 mil/WAR in 2019, every win above 0.5 WAR: 10 mil/WAR
            # catchers between 0 and 2 war: 5 mil/WAR in 2019, every win above 2 WAR: 10 mil/WAR
            # players between 0 and 2 WAR: 6.5 mil/WAR in 2019, every win above 2 WAR: 10 mil/WAR
            # increases by 0.4 mil/WAR each year
        current_age = round(float(current_age),0)
        age_multiplier = 1
        war_val = 0
        dollar_val = 0
        est_total_salary = 0
        est_raw_surplus = 0
        est_present_surplus = 0

        preseason_war_val = 0
        preseason_dollar_val = 0
        preseason_total_salary = 0
        preseason_raw_surplus = 0
        preseason_present_surplus = 0

        for yr in range (0, years_remaining):
            proj_age = current_age + yr

            if yr == 0:
                age_multiplier = 1
            elif position in ('sp', 'rp'):
                age_multiplier *= (1-((0.97**(proj_age))*(proj_age-25))/8)
            else:
                age_multiplier *= (1-((0.95**(proj_age))*(proj_age-26))/10)

            year_war = min(max(current_war,0)*age_multiplier, 10)

            if position == 'rp':
                dollar_multiplier = (4.0 + yr*0.4)
                year_dollar = min(year_war, 0.5) * dollar_multiplier + max(year_war-0.5, 0) * (dollar_multiplier+6.0)
            if position == 'c':
                dollar_multiplier = (5.0 + yr*0.4)
                year_dollar = min(year_war, 2) * dollar_multiplier + max(year_war-2, 0) * (dollar_multiplier+5.0)
            else:
                dollar_multiplier = (6.5 + yr*0.4)
                year_dollar = min(year_war, 2) * dollar_multiplier + max(year_war-2, 0) * (dollar_multiplier+3.5)

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

            preseason_war_val += year_war
            preseason_dollar_val += year_dollar
            preseason_total_salary += est_year_salary
            preseason_raw_surplus += est_year_surplus

            preseason_present_surplus += est_year_surplus*(0.92**yr)

            print '\t', year+yr, ': ', current_age, current_war, '|||', round(proj_age, 1), round(year_war, 1), round(age_multiplier, 2), '|||', round(year_dollar, 3), round(dollar_multiplier, 3), '|||', round(est_year_salary, 3), round(est_year_surplus, 3), round(preseason_present_surplus, 3), season_pct_multiplier

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




        # print war_val
        return war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus


    if contract_year not in ('V', 'CE', 'MLI'):
        contract = 'NonVet'
    else:
        contract = 'Vet'

    if adj_FV is not None:
        adj_FV = float(adj_FV)
        age = float(age)
        if position in ('sp', 'rp'):
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
        preseason_war_val = war_val
        # print '\n', entry, adj_FV, war_val, '\n'

        if contract_year not in ('V', 'CE', 'MLI'):
            year_dollar = (7.5 + (year-2019)*0.4) * year_war_avg

            war_val = 0
            dollar_val = 0
            est_total_salary = 0
            est_raw_surplus = 0

            preseason_war_val = 0
            preseason_total_salary = 0

            for yr_indx in range (6-years_remaining, 6):
                for k, v in years_map.items():
                    val_multiplier, indx, ceiling, floor = v[1], v[2], v[3], v[4]

                    if yr_indx == indx:
                        year_war = year_war_avg
                        est_year_salary = min(min(max(val_multiplier * year_dollar, floor), ceiling), year_dollar)

                        preseason_war_val += year_war
                        preseason_total_salary += est_year_salary

                        if yr_indx == 6-years_remaining and salary_counted == 'Y':
                            year_war = year_war_avg*season_pct_multiplier
                            est_year_salary = est_year_salary*season_pct_multiplier


                        print year_war, est_year_salary, year_dollar, season_pct_multiplier
                        war_val += year_war
                        est_total_salary += est_year_salary
                        # print yr_indx, year_dollar, val_multiplier, est_year_salary

        else:
            est_total_salary = salary*years_remaining
            preseason_total_salary = est_total_salary

        # for zips players, we have an estimate for $/war each season, but for prospects, we treat it as a lump sum (since we don't know how their projected war will be dispersed) (7.5 is the current $/WAR, and 0.4 is the inflation multiplier for future season)
        dollar_val = (7.5 + (year-2019)*0.4) * war_val
        preseason_dollar_val = (7.5 + (year-2019)*0.4) * preseason_war_val
        
        preseason_raw_surplus = preseason_dollar_val - preseason_total_salary
        preseason_present_surplus = preseason_raw_surplus

        est_raw_surplus = dollar_val - est_total_salary
        est_present_surplus = est_raw_surplus

        if model_war is not None:
            temp_war_val, temp_dollar_val, temp_est_total_salary, temp_est_raw_surplus, temp_est_present_surplus, temp_preseason_war_val, temp_preseason_dollar_val, temp_preseason_total_salary, temp_preseason_raw_surplus, temp_preseason_present_surplus = age_curve(age, position, model_war, years_remaining, salary, salary_counted, season_pct_multiplier, contract)

            if temp_war_val > war_val:
                war_val = temp_war_val
                dollar_val = temp_dollar_val
                est_total_salary = temp_est_total_salary
                est_raw_surplus = temp_est_raw_surplus
                est_present_surplus = temp_est_present_surplus

            if temp_preseason_war_val > preseason_war_val:
                preseason_war_val = temp_preseason_war_val
                preseason_dollar_val = temp_preseason_dollar_val
                preseason_total_salary = temp_preseason_total_salary
                preseason_raw_surplus = temp_preseason_raw_surplus
                preseason_present_surplus = temp_preseason_present_surplus

    else:
        war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus = age_curve(age, position, model_war, years_remaining, salary, salary_counted, season_pct_multiplier, contract)

    return war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus


def team_values(year):


    qry = """SET SESSION group_concat_max_len = 1000000;
    DROP TABLE IF EXISTS _trade_value_teams;
    CREATE TABLE _trade_value_teams AS
    SELECT year
    , season_gp
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

    , SUM(preseason_war_remaining) AS preseason_war
    , SUM(preseason_value) AS preseason_value
    , SUM(preseason_salary) AS preseason_salary
    , SUM(preseason_raw_surplus) AS preseason_raw_surplus
    , SUM(preseason_net_present_value) AS preseason_net_present_value

    , GROUP_CONCAT(DISTINCT CONCAT(
        player_name
        , ' ($', ifnull(est_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, '/', scaledWAR, ' zWAR/scaledWAR'))
        , ')'
        ) ORDER BY est_net_present_value DESC SEPARATOR '
'
    ) AS all_player_values

    , GROUP_CONCAT(DISTINCT CONCAT(
        player_name
        , ' ($', ifnull(preseason_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, '/', scaledWAR, ' zWAR/scaledWAR'))
        , ')'
        ) ORDER BY preseason_net_present_value DESC SEPARATOR '
'
    ) AS all_player_preseason_values

    , GROUP_CONCAT(IF(adj_FV IS NOT NULL, CONCAT(
        player_name
        , ' ($', ifnull(est_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, '/', scaledWAR, ' zWAR/scaledWAR'))
        , ')'
        ), NULL) ORDER BY est_net_present_value DESC SEPARATOR '
'
    ) AS prospect_values

    , GROUP_CONCAT(IF(adj_FV IS NULL AND zWAR IS NOT NULL, CONCAT(
        player_name
        , ' ($', ifnull(est_net_present_value, 0)
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, '/', scaledWAR, ' zWAR/scaledWAR'))
        , ')'
        ), NULL) ORDER BY est_net_present_value DESC SEPARATOR '
'
    ) AS MLB_player_values

    , GROUP_CONCAT(IF(est_value IS NULL, CONCAT(
        player_name
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, '/', scaledWAR, ' zWAR/scaledWAR'))
        , ')'
        ), NULL) SEPARATOR '
'
    ) AS missing_player_values

    FROM _trade_value tv
    JOIN(
        SELECT DISTINCT year, season_gp
        FROM _trade_value
    ) a USING (year, season_gp)
    WHERE 1
    GROUP BY year, season_gp, team_abb
    ;"""

    query = qry
    # raw_input(query)

    for q in query.split(';')[:-1]:
        # raw_input(q)
        db.query(q)
        db.conn.commit()


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2019)
    args = parser.parse_args()
    
    process(args.year)
    

