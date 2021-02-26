from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
from time import time

import sys
sys.path.append('/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/team_strength')

import trade_value as tv

db = db('NSBL')

# run zips_scraper first, then this, then zips_prep_FA


def process():
    print 'zips_FA_contract_value'
    db.query("DELETE FROM zips_FA_contract_value_batters;")
    db.query("DELETE FROM zips_FA_contract_value_pitchers;")
    batters()
    pitchers()

def batters():
    query = """SELECT c.year
    , c.Player
    , c.team_abb
    , c.post_date
    , c.age
    , c.PO
    , COALESCE(c.PA, r.PA) AS pa
    , r.WAR
    , CASE 
        WHEN COALESCE(c.PA, r.PA) IS NOT NULL
            THEN
                CASE
                    WHEN PO = 'C'
                        THEN 450*r.WAR/COALESCE(c.PA, r.PA)
                    ELSE 600*r.WAR/COALESCE(c.PA, r.PA)
                END
            ELSE WAR
        END
    AS ScaledWAR
    FROM(
        SELECT *
        FROM zips_fangraphs_batters_counting a
        LEFT JOIN NSBL.name_mapper nm ON (1
            AND a.player = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= a.year)
            AND (nm.end_year IS NULL OR nm.end_year >= a.year)
            AND (nm.position = '' OR nm.position = a.PO)
            AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
            # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
        )
    ) c
    JOIN (
        SELECT *
        FROM zips_fangraphs_batters_rate b
        LEFT JOIN NSBL.name_mapper nm ON (1
            AND b.player = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= b.year)
            AND (nm.end_year IS NULL OR nm.end_year >= b.year)
            # AND (nm.position = '' OR nm.position = b.PO)
            AND (nm.rl_team = '' OR nm.rl_team = b.team_abb)
            # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
        )
    ) r ON (1
        AND c.year = r.year
        AND c.team_abb = r.team_abb
        AND IFNULL(CONCAT(c.right_fname, ' ', c.right_lname), c.player) = IFNULL(CONCAT(r.right_fname, ' ', r.right_lname), r.player) 
    )
    ;"""

    res = db.query(query)

    for row in res:
        entry = {}
        year, Player, team_abb, post_date, age, PO, pa, WAR, ScaledWAR = row

        model_war = (float(WAR) + float(ScaledWAR))/2

        entry['year'] = year
        entry['Player'] = Player
        entry['team_abb'] = team_abb
        entry['post_date'] = post_date
        entry['age'] = age
        entry['PO'] = PO
        entry['pa'] = pa
        entry['WAR'] = WAR
        entry['model_war'] = model_war
        for contract_length in range(1,9):
            entry_str = 'yr' + str(contract_length)


            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, prospect_war_val, prospect_dollar_val, prospect_total_salary, prospect_raw_surplus, prospect_present_surplus, preseason_payout, est_payout, prospect_payout, cur_year_mlb_value, cur_year_mlb_surplus = tv.get_war_val(year = year, adj_FV = None, age = age, position = PO, model_war = model_war, years_remaining = contract_length, salary = 0.000, contract_year = 'V', expires = year+contract_length, opt = 'N', salary_counted = 'Y', season_pct_multiplier = 1.000, player_name = Player, team_abb = 'FA', rl_team = team_abb)

            entry[entry_str+'_WAR'] = war_val
            entry[entry_str+'_value'] = dollar_val

        db.insertRowDict(entry, 'zips_FA_contract_value_batters', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()
        # print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
        # for i, v in entry.items():
        #     print i, '\t', v
        # raw_input('doe')

def pitchers():
    query = """SELECT c.year
    , c.Player
    , c.team_abb
    , c.post_date
    , c.age
    , IF(GS/G >= 0.80 OR GS >= 20, 'SP', 'RP') AS PO
    , c.G
    , c.GS
    , r.WAR
    , IF(GS/G >= 0.80 OR GS >= 20, 32*r.WAR/c.GS, r.WAR) AS ScaledWAR
    FROM(
        SELECT *
        FROM zips_fangraphs_pitchers_counting a
        LEFT JOIN NSBL.name_mapper nm ON (1
            AND a.player = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= a.year)
            AND (nm.end_year IS NULL OR nm.end_year >= a.year)
            # AND (nm.position = '' OR nm.position = a.PO)
            AND (nm.rl_team = '' OR nm.rl_team = a.team_abb)
            # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
        )
    ) c
    JOIN (
        SELECT *
        FROM zips_fangraphs_pitchers_rate b
        LEFT JOIN NSBL.name_mapper nm ON (1
            AND b.player = nm.wrong_name
            AND (nm.start_year IS NULL OR nm.start_year <= b.year)
            AND (nm.end_year IS NULL OR nm.end_year >= b.year)
            # AND (nm.position = '' OR nm.position = b.PO)
            AND (nm.rl_team = '' OR nm.rl_team = b.team_abb)
            # AND (nm.nsbl_team = '' OR nm.nsbl_team = rbp.team_abb)
        )
    ) r ON (1
        AND c.year = r.year
        AND c.team_abb = r.team_abb
        AND IFNULL(CONCAT(c.right_fname, ' ', c.right_lname), c.player) = IFNULL(CONCAT(r.right_fname, ' ', r.right_lname), r.player) 
    )
    ;"""

    res = db.query(query)

    for row in res:
        entry = {}
        year, Player, team_abb, post_date, age, PO, G, GS, WAR, ScaledWAR = row

        model_war = (float(WAR) + float(ScaledWAR))/2

        entry['year'] = year
        entry['Player'] = Player
        entry['team_abb'] = team_abb
        entry['post_date'] = post_date
        entry['age'] = age
        entry['PO'] = PO
        entry['G'] = G
        entry['GS'] = GS
        entry['WAR'] = WAR
        entry['model_war'] = model_war
        for contract_length in range(1,9):
            entry_str = 'yr' + str(contract_length)

            # raw_input(year)
            war_val, dollar_val, est_total_salary, est_raw_surplus, est_present_surplus, preseason_war_val, preseason_dollar_val, preseason_total_salary, preseason_raw_surplus, preseason_present_surplus, prospect_war_val, prospect_dollar_val, prospect_total_salary, prospect_raw_surplus, prospect_present_surplus, preseason_payout, est_payout, prospect_payout = tv.get_war_val(year = year, adj_FV = None, age = age, position = PO, model_war = model_war, years_remaining = contract_length, salary = 0.000, contract_year = 'V', expires = year+contract_length, opt = 'N', salary_counted = 'Y', season_pct_multiplier = 1.000, player_name = Player, team_abb = 'FA', rl_team = team_abb)

            entry[entry_str+'_WAR'] = war_val
            entry[entry_str+'_value'] = dollar_val

        db.insertRowDict(entry, 'zips_FA_contract_value_pitchers', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()
        # print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
        # for i, v in entry.items():
        #     print i, '\t', v
        # raw_input('doe')


if __name__ == "__main__":        
    parser = argparse.ArgumentParser()

    # parser.add_argument("--year",type=int,default=2020)
    args = parser.parse_args()
    
    process()


