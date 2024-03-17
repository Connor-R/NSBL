from py_db import db
import argparse
from time import time
import re


# script to calculate player strength at every position for OOTP players


db = db('OOTP')


def process():
    start_time = time()

    i = 0 

    process_players()


def indent(s, num_spaces):
    return re.sub(r'^', ' ' * num_spaces, s, flags=re.MULTILINE)

def process_players():

    query = """drop temporary table if exists player1;
        create temporary table player1 (index idx(player_id, position, player_name))
        as
        select p.player_id
        , concat(p.first_name, ' ', p.last_name) as player_name
        , lp.position
        from players p
        join(
            select 'C' as position
            union select '1B'
            union select '2B'
            union select '3B'
            union select 'SS'
            union select 'LF'
            union select 'CF'
            union select 'RF'
            union select 'DH'
        ) lp on (if(p.position = 1, lp.position = 'DH', 1))
        where p.player_id = 1
        ;
    """

    query += """drop temporary table if exists player2;
        create temporary table player2
        as
        select p.player_name
        , p2.historical_id
        , concat(t.name, ' ', t.nickname) as team
        , concat(t2.name, ' ', t2.nickname) as parent_team
        , p.position as target_position
        , p2.position as listed_position
        , p2.age
        , case 
            when p2.bats = 1 then 'R'
            when p2.bats = 2 then 'L'
            when p2.bats = 3 then 'S'
            else 'ERROR'
        end as bats
        , case 
            when p2.throws = 1 then 'R'
            when p2.throws = 2 then 'L'
            when p2.throws = 3 then 'S'
            else 'ERROR'
        end as throws
        , p2.height

        , case
            when p.position in ('1B', '2B', '3B', 'SS') then pf.fielding_ratings_infield_range
            when p.position in ('LF', 'CF', 'RF') then pf.fielding_ratings_outfield_range
            else NULL
        end as position_range

        , case
            when p.position in ('1B', '2B', '3B', 'SS') then pf.fielding_ratings_infield_error
            when p.position in ('LF', 'CF', 'RF') then pf.fielding_ratings_outfield_error
            else NULL
        end as position_error

        , case
            when p.position = 'C' then pf.fielding_ratings_catcher_arm
            when p.position in ('1B', '2B', '3B', 'SS') then pf.fielding_ratings_infield_arm
            when p.position in ('LF', 'CF', 'RF') then pf.fielding_ratings_outfield_arm
            else NULL
        end as position_arm

        , pf.fielding_ratings_catcher_ability as catcher_ability
        , pf.fielding_ratings_catcher_arm as catcher_arm
        , pf.fielding_ratings_infield_range as infielder_range
        , pf.fielding_ratings_infield_error as infielder_error
        , pf.fielding_ratings_infield_arm as infielder_arm
        , pf.fielding_ratings_turn_doubleplay as turn_double_play
        , pf.fielding_ratings_outfield_range as outfielder_range
        , pf.fielding_ratings_outfield_error as outfielder_error
        , pf.fielding_ratings_outfield_arm as outfielder_arm

        , pf.fielding_experience0 as exp_dh
        , pf.fielding_experience1 as exp_p
        , pf.fielding_experience2 as exp_c
        , pf.fielding_experience3 as exp_1b
        , pf.fielding_experience4 as exp_2b
        , pf.fielding_experience5 as exp_3b
        , pf.fielding_experience6 as exp_ss
        , pf.fielding_experience7 as exp_lf
        , pf.fielding_experience8 as exp_cf
        , pf.fielding_experience9 as exp_rf

        , pb.batting_ratings_overall_contact as contact
        , pb.batting_ratings_overall_babip as babip
        , pb.batting_ratings_overall_gap as gap_power
        , pb.batting_ratings_overall_power as power
        , pb.batting_ratings_overall_eye as eye
        , pb.batting_ratings_overall_strikeouts as avoid_k
        , pb.batting_ratings_overall_hp as hbp

        , pb.batting_ratings_vsr_contact as vsr_contact
        , pb.batting_ratings_vsr_babip as vsr_babip
        , pb.batting_ratings_vsr_gap as vsr_gap_power
        , pb.batting_ratings_vsr_power as vsr_power
        , pb.batting_ratings_vsr_eye as vsr_eye
        , pb.batting_ratings_vsr_strikeouts as vsr_avoid_k
        , pb.batting_ratings_vsr_hp as vsr_hbp

        , pb.batting_ratings_vsl_contact as vsl_contact
        , pb.batting_ratings_vsl_babip as vsl_babip
        , pb.batting_ratings_vsl_gap as vsl_gap_power
        , pb.batting_ratings_vsl_power as vsl_power
        , pb.batting_ratings_vsl_eye as vsl_eye
        , pb.batting_ratings_vsl_strikeouts as vsl_avoid_k
        , pb.batting_ratings_vsl_hp as vsl_hbp

        from player1 p
        join players p2 on (p.player_id = p2.player_id)
        join players_batting pb on (pb.player_id = p.player_id)
        join players_fielding pf on (pb.player_id = pf.player_id)
        left join teams t on (pb.team_id = t.team_id)
        left join teams t2 on (t.parent_team_id = t2.team_id)
        where 1
        ;
    """

    # input(query)
    queries = query.split(';')
    for q in queries[:-1]:
        print q
        db.query(q)
        db.conn.commit()
        # raw_input('hi')

    query = add_coefficients(query)

    query = calculations(query)

    query = run_conversions(query)

    query = wins_conversions(query)



    # insert_table(query)

def add_coefficients(query):
    row = db.query("select * from player2")
    for r in row:
        raw_input(r)
    coeff_dict = { #index: [alias, type, category, target, a.name]
        1: ['eye_to_bbrate', 'offense', 'eye', 'bb_rate', 'eye']
        , 2: ['avoidk_to_krate', 'offense', 'avoid_k', 'k_rate', 'avoid_k']
        , 3: ['avoidk_to_1brate', 'offense', 'avoid_k', '1b_rate', 'avoid_k']
        , 4: ['gap_to_1brate', 'offense', 'gap_power', '1b_rate', 'gap_power']
        , 5: ['babip_to_1brate', 'offense', 'babip', '1b_rate', 'babip']
        , 6: ['avoidk_to_2brate', 'offense', 'avoid_k', '2b_rate', 'avoid_k']
        , 7: ['gap_to_2brate', 'offense', 'gap_power', '2b_rate', 'gap_power']
        , 8: ['power_to_2brate', 'offense', 'power', '2b_rate', 'power']
        , 9: ['avoidk_to_3brate', 'offense', 'avoid_k', '3b_rate', 'avoid_k']
        , 10: ['gap_to_3brate', 'offense', 'gap_power', '3b_rate', 'gap_power']
        , 11: ['power_to_3brate', 'offense', 'power', '3b_rate', 'power']
        , 12: ['power_to_hrrate', 'offense', 'power', 'hr_rate', 'power']
        , 13: ['avoidk_to_runspergame', 'offense', 'avoid_k', 'runs_per_game', 'avoid_k']
        , 14: ['babip_to_runspergame', 'offense', 'babip', 'runs_per_game', 'babip']
        , 15: ['eye_to_runspergame', 'offense', 'eye', 'runs_per_game', 'eye']
        , 16: ['gap_to_runspergame', 'offense', 'gap_power', 'runs_per_game', 'gap_power']
        , 17: ['power_to_runspergame', 'offense', 'power', 'runs_per_game', 'power']
        , 18: ['arm', 'defense', 'arm', '', 'position_arm']
        , 19: ['err', 'defense', 'error', '', 'position_error']
        , 20: ['rng', 'defense', 'range', '', 'position_range']
        , 21: ['tdp', 'defense', 'turn_dp', '', 'turn_double_play']
        , 22: ['catcher_ability', 'defense', 'catcher_ability', '', 'catcher_ability']
        , 23: ['height', 'defense', 'height', '', 'height']
    }

    query_select = "select a.*\n"

    query_join = "\n) a"
    for k, v in coeff_dict.items():
        query_select += "\n, concat(" + v[0] + ".min_range, ' to ', " + v[0] + ".max_range) as " + v[0] + "_pivot"
        query_select += "\n, a." + v[4] + " as " + v[0] + "_placeholder"
        query_select += "\n, trim(" + v[0] + ".slope)+0 as " + v[0] + "_slope"
        query_select += "\n, trim(" + v[0] + ".intercept)+0 as " + v[0] + "_intercept\n"

        join_type = 'left'
        extra_line = "\n\tand " + v[0] + ".position = a.target_position"
        if v[1] == 'offense':
            join_type = ''
            extra_line = ''
        
        query_join += "\n" + join_type + " join coefficients " + v[0] + " on (1"
        query_join += "\n\tand " + v[0] + ".type = '" + v[1] + "'"
        query_join += "\n\tand " + v[0] + ".category = '" + v[2] + "'"
        query_join += "\n\tand " + v[0] + ".target = '" + v[3] + "'"
        query_join += "\n\tand " + v[0] + ".min_range <= a." + v[4]
        query_join += "\n\tand " + v[0] + ".max_range >= a." + v[4] + extra_line
        query_join += "\n)"

    query_select += "\nfrom(\n"

    query = query_select + query + query_join

    return query


def calculations(query):
    calc_dict = { # [field_name, formula]
        1: ["hbp_per_650", "trim(b.hbp*650/550)+0"]
        , 2: ["bb_rate", "trim(b.eye_to_bbrate_placeholder*b.eye_to_bbrate_slope + b.eye_to_bbrate_intercept)+0"]
        , 3: ["k_rate", "trim(b.avoidk_to_krate_placeholder*b.avoidk_to_krate_slope + b.avoidk_to_krate_intercept)+0"]
        , 4: ["1b_rate", """trim((b.babip_to_1brate_placeholder*b.babip_to_1brate_slope + b.babip_to_1brate_intercept) 
            + (b.gap_to_1brate_placeholder*b.gap_to_1brate_slope + b.gap_to_1brate_intercept)
            - (select universal from coefficients where target = 'normalized_1b_rate')
            + (b.avoidk_to_1brate_placeholder*b.avoidk_to_1brate_slope + b.avoidk_to_1brate_intercept)
            - (select universal from coefficients where target = 'normalized_1b_rate'))+0
            """]
        , 5: ["2b_rate", """trim((b.gap_to_2brate_placeholder*b.gap_to_2brate_slope + b.gap_to_2brate_intercept)
            + (b.power_to_2brate_placeholder*b.power_to_2brate_slope + b.power_to_2brate_intercept)
            - (select universal from coefficients where target = 'normalized_2b_rate')
            + (b.avoidk_to_2brate_placeholder*b.avoidk_to_2brate_slope + b.avoidk_to_2brate_intercept)
            - (select universal from coefficients where target = 'normalized_2b_rate'))+0
        """]
        , 6: ["3b_rate", """trim((b.gap_to_3brate_placeholder*b.gap_to_3brate_slope + b.gap_to_3brate_intercept)
            + (b.power_to_3brate_placeholder*b.power_to_3brate_slope + b.power_to_3brate_intercept)
            - (select universal from coefficients where target = 'normalized_3b_rate')
            + (b.avoidk_to_3brate_placeholder*b.avoidk_to_3brate_slope + b.avoidk_to_3brate_intercept)
            - (select universal from coefficients where target = 'normalized_3b_rate'))+0
        """]
        , 7: ["hr_rate", "trim(b.power_to_hrrate_placeholder*b.power_to_hrrate_slope + b.power_to_hrrate_intercept)+0"]
        , 8: ["arm_runs", "trim(b.arm_placeholder*b.arm_slope + b.arm_intercept)+0"]
        , 9: ["error_runs", "trim(b.err_placeholder*b.err_slope + b.err_intercept)+0"]
        , 10: ["range_runs", "trim(b.rng_placeholder*b.rng_slope + b.rng_intercept)+0"]
        , 11: ["dp_runs", "trim(b.tdp_placeholder*b.tdp_slope + b.tdp_intercept)+0"]
        , 12: ["catcher_ability_runs", "trim(b.catcher_ability_placeholder*b.catcher_ability_slope + b.catcher_ability_intercept)+0"]
        , 13: ["height_runs", "trim(b.height_placeholder*b.height_slope + b.height_intercept)+0"]
    }

    query_select = "select b.*\n"

    for k, v in calc_dict.items():
        query_select += "\n, (" + v[1] + ") as " + v[0]

    query_select += "\nfrom(\n"

    query_join = "\n) b"

    query = query_select + indent(query, 4) + query_join

    return query


def run_conversions(query):

    conversion_dict = { # [field_name, formula]
        1: ["offensive_runs_per_game_IMPACT", """trim(
            ((c.1b_rate-(select universal from coefficients where target = 'normalized_1b_rate'))/0.594)
            + ((c.2b_rate-(select universal from coefficients where target = 'normalized_2b_rate'))/0.693)
            + ((c.3b_rate-(select universal from coefficients where target = 'normalized_3b_rate'))/0.0519)
            + ((c.hr_rate-(select universal from coefficients where target = 'normalized_hr_rate'))/0.219)
            + ((((c.hbp_per_650 + (650-c.hbp_per_650)*c.bb_rate - (select universal from coefficients where target = 'walks_plus_hbp_adjustment'))/650)
                - (select universal from coefficients where target = 'normalized_walk_rate'))/0.875)
            + ((c.k_rate-(select universal from coefficients where target = 'normalized_strikeout_rate'))/-1.217)
        )+0"""]
        , 2: ["defensive_runs_per_game_IMPACT", """trim( (select universal from coefficients where target = 'median_runs_per_game') * (case
                when c.target_position = 'C' then 2
                when c.target_position = '1B' then 5
                when c.target_position = '2B' then 4
                when c.target_position = '3B' then 4
                when c.target_position = 'SS' then 4
                when c.target_position = 'LF' then 3
                when c.target_position = 'CF' then 3
                when c.target_position = 'RF' then 3
            end)
            - ifnull(c.arm_runs, 0)
            - ifnull(c.error_runs, 0)
            - ifnull(c.range_runs, 0)
            - ifnull(c.dp_runs, 0)
            - ifnull(c.catcher_ability_runs, 0)
            - ifnull(c.height_runs, 0)
        )+0"""]
    }

    query_select = "select c.*\n"

    for k, v in conversion_dict.items():
        query_select += "\n, (" + v[1] + ") as " + v[0]

    query_select += "\nfrom(\n"

    query_join = "\n) c"

    query = query_select + indent(query, 4) + query_join


    #### per season
    per_season_dict = { # [field_name, formula]
        1: ["offensive_runs_created_ORC", "trim(d.offensive_runs_per_game_IMPACT*162)+0"]
        , 2: ["expected_defensive_runs_prevented_eDRP", "trim(ifnull(d.defensive_runs_per_game_IMPACT,0)*162)+0"]
    }

    query_select = "select d.*\n"

    for k, v in per_season_dict.items():
        query_select += "\n, (" + v[1] + ") as " + v[0]

    query_select += "\nfrom(\n"

    query_join = "\n) d"

    query = query_select + indent(query, 4) + query_join

    return query


def wins_conversions(query):
    wins_dict = { # [field_name, formula]
        1: ["toWAR", "trim(e.offensive_runs_created_ORC/10)+0"]
        , 2: ["tdWAA", "trim(e.expected_defensive_runs_prevented_eDRP/10)+0"]
        , 3: ["tdWAR", """trim(e.expected_defensive_runs_prevented_eDRP/10 + (case
                when e.target_position = 'C' then 1
                when e.target_position = '1B' then 0.2
                when e.target_position = '2B' then 1.3
                when e.target_position = '3B' then 1
                when e.target_position = 'SS' then 1.6
                when e.target_position = 'LF' then 0.2
                when e.target_position = 'CF' then 2.2
                when e.target_position = 'RF' then 1
                when e.target_position = 'DH' then 0
            end))+0"""
            ]
        , 4: ["sWAR", """trim(e.offensive_runs_created_ORC/10
            + e.expected_defensive_runs_prevented_eDRP/10 + (case
                when e.target_position = 'C' then 1
                when e.target_position = '1B' then 0.2
                when e.target_position = '2B' then 1.3
                when e.target_position = '3B' then 1
                when e.target_position = 'SS' then 1.6
                when e.target_position = 'LF' then 0.2
                when e.target_position = 'CF' then 2.2
                when e.target_position = 'RF' then 1
                when e.target_position = 'DH' then 0
            end))+0"""
            ]
    }

    query_select = "select e.*\n"

    for k, v in wins_dict.items():
        query_select += "\n, (" + v[1] + ") as " + v[0]

    query_select += "\nfrom(\n"

    query_join = "\n) e"

    query = query_select + indent(query, 4) + query_join

    return query


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    process()
    

