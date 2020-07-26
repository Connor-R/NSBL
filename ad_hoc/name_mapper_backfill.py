from py_db import db

import NSBL_helpers as helper

db = db("NSBL")


table_dict = {"register_batting_analytical": "a.player_name"
    , "register_batting_primary": "a.player_name"
    , "register_batting_secondary": "a.player_name"
    , "register_batting_splits": "a.player_name"
    , "register_pitching_analytical": "a.player_name"
    , "register_pitching_primary": "a.player_name"
    , "register_pitching_rates_relief": "a.player_name"
    , "register_pitching_rates_start": "a.player_name"
    , "register_pitching_secondary": "a.player_name"
    , "zips_defense": "a.player_name"
    , "zips_fangraphs_batters_counting": "a.Player"
    , "zips_fangraphs_batters_rate": "a.Player"
    , "zips_fangraphs_pitchers_counting": "a.Player"
    , "zips_fangraphs_pitchers_rate": "a.Player"
    , "zips_offense": "a.player_name"
    , "zips_offense_splits": "a.player_name"
    , "zips_pitching": "a.player_name"
    , "zips_pitching_splits": "a.player_name"
    , "mlb_prospects.fg_raw": "a.playerName"
    , "mlb_prospects.minorleagueball_professional": "a.full_name"
    , "mlb_prospects.mlb_prospects_draft": "CONCAT(a.fname, ' ', a.lname)"
    , "mlb_prospects.mlb_prospects_international": "CONCAT(a.fname, ' ', a.lname)"
    , "mlb_prospects.mlb_prospects_professional": "CONCAT(a.fname, ' ', a.lname)"
}


for k,v in table_dict.items():
    print k
    qry = """
    SELECT DISTINCT %s
    FROM %s a
    LEFT JOIN name_mapper nm ON (%s = nm.wrong_name)
    WHERE 1
        AND nm.wrong_name IS NULL
    """ % (v, k, v)

    # raw_input(qry)


    names = db.query(qry)

    for name in names:
        helper.input_name(name[0])
