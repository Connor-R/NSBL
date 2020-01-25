from py_db import db
import NSBL_helpers as helper
import argparse
from time import time



# script that estimates trade values for the ~1750 players on NSBL rosters
# it first looks for zips projections/age for a player; if those do not exists it looks for the player in the prospect database
# if neither exist, the player's trade value is null
# otherwise, it uses zips projections of prospect FV values to determine value over the length of their contract, and compares to how much the player is being paid


db = db('NSBL')

# year: [years_remaining, salary multiplied, reverse index, ceiling, floor]
# select year, contract_year, max(salary), min(salary) from excel_rosters where contract_year not in ('v', 'ce', 'mli') group by year desc, contract_year asc
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
                THEN 450*(zh.WAR/zh.z_PA)
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

        print '\n\n-------------------------------------------------------------------'
        print player_name, team_abb, position, salary, contract_year, expires, opt, age

        entry = {'year':year, 'player_name': player_name, 'fname': fname, 'lname': lname, 'team_abb': team_abb, 'position': position, 'salary': salary, 'contract_year': contract_year, 'expires': expires, 'opt': opt, 'NTC': NTC, 'salary_counted': salary_counted, 'season_gp':season_gp, 'age':age, 'adj_FV':adj_FV, 'zWAR':zWAR, 'scaledWAR': scaledWAR}

        if adj_FV is not None:
            rl_team = p_Team
        elif zWAR is not None:
            rl_team = z_Team
        else:
            rl_team = None

        # print zWAR, scaledWAR,
        if zWAR is not None:
            model_war = (float(zWAR) + float(scaledWAR))/2
        else:
            model_war = None
        # print model_war

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
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, prospect_war_val, prospect_dollar_val, prospect_total_salary, prospect_raw_surplus, prospect_present_surplus, preseason_payout, est_payout, prospect_payout = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

        else:
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, prospect_war_val, prospect_dollar_val, prospect_total_salary, prospect_raw_surplus, prospect_present_surplus, preseason_payout, est_payout, prospect_payout = get_war_val(year, adj_FV, age, position, model_war, years_remaining, salary, contract_year, expires, opt, salary_counted, season_pct_multiplier, player_name, team_abb, rl_team)

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

        entry['prospect_war_remaining'] = prospect_war_val
        entry['prospect_value'] = prospect_dollar_val
        entry['prospect_salary'] = prospect_total_salary
        entry['prospect_raw_surplus'] = prospect_raw_surplus
        entry['prospect_net_present_value'] = prospect_present_surplus

        entry['est_payout'] = est_payout
        entry['preseason_payout'] = preseason_payout
        entry['prospect_payout'] = prospect_payout

        # for k,v in entry.items():
        #     print k, v
        # print entry

        db.insertRowDict(entry, '_trade_value', insertMany=False, replace=True, rid=0, debug=1)
        db.conn.commit()

def get_war_val(year, adj_FV, age, position, model_war, years_remaining, salary, contract_year, expires, opt, salary_counted, season_pct_multiplier, player_name, team_abb, rl_team):
    preseason_payout, est_payout, prospect_payout = None, None, None
    prospect_war_val = None
    prospect_dollar_val = None
    prospect_total_salary = None
    prospect_raw_surplus = None
    prospect_present_surplus = None

    salary = float(salary)
    if model_war is not None:
        model_war = float(model_war)

    def age_curve(current_age, position, current_war, years_remaining, salary, salary_counted, season_pct_multiplier, player_name, team_abb, rl_team, contract='Vet'):


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

        payout = player_name.upper() + ': ' + str(current_age) + ' yrs ' + str(position.upper()) + ' (' + team_abb.upper() + ' | ' + rl_team.upper() +  ') - %s\nContract: ' + str(contract) + ' w/' + str(years_remaining) + ' years remaining |  Current Salary: $' + str(round(salary, 3)) + ' (' + str(salary_counted) + ' counted)\n'

        preseason_payout = payout % ('PRESEASON PAYOUT')
        est_payout = payout % ('EST PAYOUT')

        for yr in range (0, years_remaining):
            proj_age = current_age + yr

            # curve value is a decay function with "peak" age (age_multiplier = 1) at 26 for hitters and 25 for pitchers. The pitcher curve is steeper
            if yr == 0:
                age_multiplier = 1
            elif position in ('sp', 'rp'):
                age_multiplier *= (1-((0.97**(proj_age))*(proj_age-25))/8)
            else:
                age_multiplier *= (1-((0.95**(proj_age))*(proj_age-26))/10)

            year_war = min(max(current_war,0)*age_multiplier, 10)


            # dollar_value:
                # rps: between 0 and 0.2 WAR: 2 mil/WAR
                    # between 0.2 and 0.4 WAR: 4 mil/WAR
                    # every win above 0.4 WAR: 8 mil/WAR
                # sps: between 0 and 0.5 WAR: 2 mil/WAR
                    # between 0.5 and 1.0 WAR: 4 mil/WAR
                    # every win above 1.0 WAR: 8 mil/WAR
                # catchers: between 0 and 0.5 WAR: 2 mil/WAR
                    # between 0.5 and 1.5 WAR: 4 mil/WAR
                    # every win above 1.5 WAR: 8 mil/WAR
                # others: between 0 and 0.5 WAR: 2 mil/WAR
                    # between 0.5 and 1.5 WAR: 6 mil/WAR
                    # every win above 1.5 WAR: 9 mil/WAR
            if position == 'rp':
                dollar_multiplier = (2.0 + yr*0.4)
                if year_war <= 0.2:
                    year_dollar = min(year_war, 0.2)*dollar_multiplier
                elif year_war > 0.2 and year_war <= 0.4:
                    year_dollar = 2*(0.2) + (year_war-0.2)*(dollar_multiplier+2)
                elif year_war > 0.4:
                    year_dollar = 2*(0.2) + 4*(0.4-0.2) + (year_war-0.4)*(dollar_multiplier+6)
            elif position == 'sp':
                dollar_multiplier = (2.0 + yr*0.4)
                if year_war <= 0.5:
                    year_dollar = min(year_war, 0.5)*dollar_multiplier
                elif year_war > 0.5 and year_war <= 1.0:
                    year_dollar = 2*(0.5) + (year_war-0.5)*(dollar_multiplier+2)
                elif year_war > 1.0:
                    year_dollar = 2*(0.5) + (dollar_multiplier+2)*(1.0-0.5) + (year_war-1.0)*(dollar_multiplier+6)
            elif position == 'c':
                dollar_multiplier = (2.0 + yr*0.4)
                if year_war <= 0.5:
                    year_dollar = min(year_war, 0.5)*dollar_multiplier
                elif year_war > 0.5 and year_war <= 1.5:
                    year_dollar = 2*(0.5) + (year_war-0.5)*(dollar_multiplier+2)
                elif year_war > 1.5:
                    year_dollar = 2*(0.5) + (dollar_multiplier+2)*(1.5-0.5) + (year_war-1.5)*(dollar_multiplier+6)
            else:
                dollar_multiplier = (2.0 + yr*0.4)
                if year_war <= 0.5:
                    year_dollar = min(year_war, 0.5)*dollar_multiplier
                elif year_war > 0.5 and year_war <= 1.5:
                    year_dollar = 2*(0.5) + (year_war-0.5)*(dollar_multiplier+4)
                elif year_war > 1.5:
                    year_dollar = 2*(0.5) + (dollar_multiplier+4)*(1.5-0.5) + (year_war-1.5)*(dollar_multiplier+7)

            if contract != 'Vet':
                for k, v in years_map.items():
                    val_multiplier, indx, ceiling, floor = v[1], v[0], v[3], v[4]
                    if yr == 0:
                        est_year_salary = salary 
                        if salary_counted == 'Y':
                            est_year_surplus = year_dollar - est_year_salary
                        else:
                            est_year_surplus = max(year_dollar - est_year_salary, 0)
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

            # 8% discount rate (0.92^n)
            preseason_present_surplus += est_year_surplus*(0.92**yr)

            if yr == 0:
                txt_add = ' (' + str(season_pct_multiplier) + '% remaining)'
            else:
                preseason_payout += '\n'
                est_payout += '\n'
                txt_add = ''

            preseason_payout += '\nYear: ' + str(year+yr)
            preseason_payout += ' | Age: ' + str(round(proj_age, 1)) + ' (age curve: ' + str(round(age_multiplier, 2)) + ')'
            preseason_payout += ' | zWAR: ' + str(round(year_war, 1))
            preseason_payout += ' | Year value: $' + str(round(year_dollar, 1))
            preseason_payout += ' (Inflation: +$' + str(yr*0.4) + ')' 
            preseason_payout += '\n\t\tEst salary: $' + str(round(est_year_salary, 1))
            preseason_payout += ' | Raw year surplus: $' + str(round(est_year_surplus, 1)) 
            preseason_payout += ' (PV discount: ' + str(100*round(0.92**yr, 2)) + '%)'
            preseason_payout += ' | Rolling surplus: $' + str(round(preseason_present_surplus, 1))

            # print preseason_payout

            if yr == 0 and salary_counted == 'Y':
                year_war = year_war*season_pct_multiplier
                est_year_salary = est_year_salary*season_pct_multiplier
                est_year_surplus = est_year_surplus*season_pct_multiplier
                year_dollar = year_dollar*season_pct_multiplier

            war_val += year_war
            dollar_val += year_dollar
            est_total_salary += est_year_salary
            est_raw_surplus += est_year_surplus

            est_year_present_surplus = est_year_surplus*(0.92**yr)
            est_present_surplus += est_year_present_surplus

            est_payout += '\nYear: ' + str(year+yr) + txt_add
            est_payout += ' | Age: ' + str(round(proj_age, 1)) + ' (age curve: ' + str(round(age_multiplier, 2)) + ')'
            est_payout += ' | zWAR: ' + str(round(year_war, 1))
            est_payout += ' | Year value: $' + str(round(year_dollar, 1)) 
            est_payout += ' (Inflation: +$' + str(yr*0.4) + ')' 
            est_payout += '\n\t\tEst salary: $' + str(round(est_year_salary, 1))
            est_payout += ' | Raw year surplus: $' + str(round(est_year_surplus, 1)) 
            est_payout += ' (PV discount: ' + str(100*round(0.92**yr, 2)) + '%)'
            est_payout += ' | Rolling surplus: $' + str(round(est_present_surplus, 1))

        est_payout += '\n\nSum salary: $' + str(round(est_total_salary, 1))
        est_payout += ' | Sum WAR: ' + str(round(war_val, 1))
        est_payout += ' | Sum value: $' + str(round(dollar_val, 1))
        est_payout += ' | Sum surplus: $' + str(round(est_present_surplus, 1))

        preseason_payout += '\n\nSum salary: $' + str(round(preseason_total_salary, 1))
        preseason_payout += ' | Sum WAR: ' + str(round(preseason_war_val, 1))
        preseason_payout += ' | Sum value: $' + str(round(preseason_dollar_val, 1))
        preseason_payout += ' | Sum surplus: $' + str(round(preseason_present_surplus, 1))


        print preseason_payout
        print est_payout


        # print war_val
        return war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, preseason_payout, est_payout


    if contract_year not in ('V', 'CE', 'MLI'):
        contract = 'NonVet'
    else:
        contract = 'Vet'

    if adj_FV is not None:
        adj_FV = float(adj_FV)
        age = float(age)
        if position in ('sp', 'rp'):
            if adj_FV <= 38:
                war_val = 0.1
            elif adj_FV > 38 and adj_FV <= 46:
                war_val = 0.1 + (adj_FV-38)*0.1
            elif adj_FV > 46:
                war_val = 0.9 + (adj_FV-46)*0.35
        else:
            if adj_FV <= 35:
                war_val = 0.1
            elif adj_FV > 35 and adj_FV <= 47:
                war_val = 0.1 + (adj_FV-35)*0.1
            elif adj_FV > 47:
                war_val = 1.3 + (adj_FV-47)*0.40
        year_war_avg = ((war_val) / 6)
        preseason_war_val = ((war_val) / 6)*(years_remaining)
        # print '\n', entry, adj_FV, war_val, '\n'
        if rl_team is None:
            rl_team_txt = ''
        else:
            rl_team_txt = rl_team.upper()

        prospect_payout = player_name.upper() + ': ' + str(position).upper() + ' (' + team_abb.upper() + ' | ' + rl_team_txt +  ') - PROSPECT PAYOUT\nContract: ' + str(contract) + ' w/' + str(years_remaining) + ' years remaining |  Current Salary: $' + str(round(salary, 3)) + ' (' + str(salary_counted) + ' counted)'
        prospect_payout += '\nadjFV: ' + str(round(adj_FV, 1)) + ' | projWAR: ' + str(round(year_war_avg*years_remaining, 1))
        prospect_payout += ' ( avgWAR: ' + str(round(year_war_avg, 1)) + ')\n'

        if contract_year not in ('V', 'CE', 'MLI'):
            # cost for prospects is higher to account for volatility as well as stashability
            year_dollar = (12.5 + (year-2019)*0.4) * year_war_avg

            war_val = 0
            dollar_val = 0
            est_total_salary = 0
            est_raw_surplus = 0

            preseason_war_val = 0
            preseason_dollar_val = 0
            preseason_total_salary = 0

            for yr_indx in range (6-years_remaining, 6):
                for k, v in years_map.items():
                    val_multiplier, indx, ceiling, floor = v[1], v[2], v[3], v[4]

                    if yr_indx == indx:
                        year_war = year_war_avg
                        est_year_salary = min(min(max(val_multiplier * year_dollar, floor), ceiling), year_dollar)

                        preseason_war_val += year_war
                        preseason_dollar_val += year_dollar
                        preseason_total_salary += est_year_salary

                        txt_add = ''
                        if yr_indx == 6-years_remaining and salary_counted == 'Y':
                            year_war2 = year_war_avg*season_pct_multiplier
                            year_dollar2 = year_dollar*season_pct_multiplier
                            est_year_salary2 = est_year_salary*season_pct_multiplier
                            txt_add2 = ' (' + str(season_pct_multiplier) + '% remaining)'
                            war_val += year_war2
                            dollar_val += year_dollar2
                            est_total_salary += est_year_salary2
                            est_raw_surplus += year_dollar2-est_year_salary2

                            prospect_payout += '\nYear: +' + str(indx) + txt_add2
                            prospect_payout += ' | projWAR: ' + str(round(year_war2, 1))
                            prospect_payout += ' | Year value: $' + str(round(year_dollar2, 1))
                            prospect_payout += ' | PRESEASON - '
                            prospect_payout += 'projWAR: ' + str(round(year_war, 1))
                            prospect_payout += ' | Year value: $' + str(round(year_dollar, 1)) 
                            prospect_payout += '\n\t\tEst Salary: $' + str(round(est_year_salary2, 1))
                            prospect_payout += ' | Year surplus: $' + str(round(year_dollar2-est_year_salary2, 1)) 
                            prospect_payout += ' | PRESEASON - '
                            prospect_payout += 'Est Salary: $' + str(round(est_year_salary, 1))
                            prospect_payout += ' | Year surplus: $' + str(round(year_dollar-est_year_salary, 1)) 
                        else:
                            war_val += year_war_avg
                            dollar_val += year_dollar
                            est_total_salary += est_year_salary
                            est_raw_surplus += year_dollar-est_year_salary

                            prospect_payout += '\nYear: +' + str(indx) + txt_add
                            prospect_payout += ' | projWAR: ' + str(round(year_war, 1))
                            prospect_payout += ' | Year value: $' + str(round(year_dollar, 1)) 
                            prospect_payout += '\n\t\tEst Salary: $' + str(round(est_year_salary, 1))
                            prospect_payout += ' | Year surplus: $' + str(round(year_dollar-est_year_salary, 1)) 

        else:
            preseason_total_salary = salary*years_remaining
            preseason_dollar_val = (12.5 + (year-2019)*0.4) * preseason_war_val

            prospect_payout += '\nPreseason salary: $' + str(round(preseason_total_salary, 1))
            prospect_payout += ' | Preseason value: $' + str(round(preseason_dollar_val, 1))

            est_total_salary = salary*(years_remaining-1) + (salary*season_pct_multiplier)
            war_val = (year_war_avg*(years_remaining-1) + year_war_avg*season_pct_multiplier)
            dollar_val = (12.5 + (year-2019)*0.4) *war_val

            prospect_payout += '\nEst salary: $' + str(round(est_total_salary, 1))
            prospect_payout += ' | Est value: $' + str(round(dollar_val, 1))


        preseason_raw_surplus = preseason_dollar_val - preseason_total_salary
        preseason_present_surplus = preseason_raw_surplus

        est_raw_surplus = dollar_val - est_total_salary
        est_present_surplus = est_raw_surplus


        prospect_payout += '\n\nEST MODEL:\nSum salary: $' + str(round(est_total_salary, 1))
        prospect_payout += ' | Sum WAR: ' + str(round(war_val, 1))
        prospect_payout += ' | Sum value: $' + str(round(dollar_val, 1))
        prospect_payout += ' | Sum surplus: $' + str(round(est_present_surplus, 1))

        prospect_payout += '\nPRESEASON MODEL:\nSum salary: $' + str(round(preseason_total_salary, 1))
        prospect_payout += ' | Sum WAR: ' + str(round(preseason_war_val, 1))
        prospect_payout += ' | Sum value: $' + str(round(preseason_dollar_val, 1))
        prospect_payout += ' | Sum surplus: $' + str(round(preseason_present_surplus, 1))

        print prospect_payout

        prospect_war_val = preseason_war_val
        prospect_dollar_val = preseason_dollar_val
        prospect_total_salary = preseason_total_salary
        prospect_raw_surplus = preseason_present_surplus
        prospect_present_surplus = preseason_present_surplus

        if model_war is not None:
            temp_war_val, temp_dollar_val, temp_est_total_salary, temp_est_raw_surplus, temp_est_present_surplus, temp_preseason_war_val, temp_preseason_dollar_val, temp_preseason_total_salary, temp_preseason_raw_surplus, temp_preseason_present_surplus, preseason_payout, est_payout = age_curve(age, position, model_war, years_remaining, salary, salary_counted, season_pct_multiplier, player_name, team_abb, rl_team, contract)

            if temp_est_present_surplus > est_present_surplus:
                war_val = temp_war_val
                dollar_val = temp_dollar_val
                est_total_salary = temp_est_total_salary
                est_raw_surplus = temp_est_raw_surplus
                est_present_surplus = temp_est_present_surplus

            if temp_preseason_present_surplus > preseason_present_surplus:
                preseason_war_val = temp_preseason_war_val
                preseason_dollar_val = temp_preseason_dollar_val
                preseason_total_salary = temp_preseason_total_salary
                preseason_raw_surplus = temp_preseason_raw_surplus
                preseason_present_surplus = temp_preseason_present_surplus

    else:
        war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, preseason_payout, est_payout = age_curve(age, position, model_war, years_remaining, salary, salary_counted, season_pct_multiplier, player_name, team_abb, rl_team, contract)

    return war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, prospect_war_val, prospect_dollar_val, prospect_total_salary, prospect_raw_surplus, prospect_present_surplus, preseason_payout, est_payout, prospect_payout


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

    , SUM(prospect_war_remaining) AS prospect_war
    , SUM(prospect_value) AS prospect_value
    , SUM(prospect_salary) AS prospect_salary
    , SUM(prospect_raw_surplus) AS prospect_raw_surplus
    , SUM(prospect_net_present_value) AS prospect_net_present_value

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
        ) ORDER BY est_net_present_value DESC SEPARATOR ' /
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
        ) ORDER BY preseason_net_present_value DESC SEPARATOR ' /
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
        ), NULL) ORDER BY est_net_present_value DESC SEPARATOR ' /
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
        ), NULL) ORDER BY est_net_present_value DESC SEPARATOR ' /
'
    ) AS MLB_player_values

    , GROUP_CONCAT(IF(est_value IS NULL, CONCAT(
        player_name
        , ', ', IFNULL(age, ''), ' - ', UPPER(position)
        , ', $', salary, ' - ', contract_year, IF(expires>0, CONCAT(' ', expires), ''), IF(opt='Y', '+1', '')
        , IF(adj_FV is NULL, '', CONCAT(', ', adj_FV, ' adjFV'))
        , IF(zWAR is NULL, '', CONCAT(', ', zWAR, '/', scaledWAR, ' zWAR/scaledWAR'))
        , ')'
        ), NULL) SEPARATOR ' /
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
    
