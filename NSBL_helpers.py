# A set of helper functions for the NSBL codebase
from py_db import db
db = db('NSBL')



def get_team_abb(team_name, year):
    qry = db.query("SELECT team_abb FROM teams WHERE year = %s AND team_name = '%s';" % (year, team_name))
    if qry != ():
        team_abb = qry[0][0]
    else:
        print "\n\n!!!!ERROR!!!! - no team_abb for %s, %s" % (year, team_name)
        team_abb = None

    return team_abb

def get_division(team_name, year):
    division_dict = {
    }

    qry = """SELECT team_name
    , division
    FROM teams
    WHERE 1
        AND year = %s
    ;""" % (year)

    res = db.query(qry)
    for row in res:
        tm, div = row
        division_dict[tm] = div

    division = division_dict.get(team_name)

    divisional_teams = []
    conference_teams = []
    non_conference_teams = []
    for k,v in division_dict.items():
        if v == division and k != team_name:
            divisional_teams.append(k)
        if v[:2] == division[:2] and k != team_name:
            conference_teams.append(k)
        if v[:2] != division[:2]:
            non_conference_teams.append(k)

    return division, divisional_teams, conference_teams, non_conference_teams

def get_team_name(city_name, year):
    qry = db.query("SELECT team_name FROM teams WHERE year = %s AND city_name = '%s';" % (year, city_name))
    if qry != ():
        team_name = qry[0][0]
    else:
        print "\n\n!!!!ERROR!!!! - no team_name for %s, %s" % (year, city_name)
        team_name = None

    return team_name

def get_mascot_names(team_abb, year):
    qry = db.query("SELECT mascot_name FROM teams WHERE year = %s AND team_abb = '%s';" % (year, team_abb))
    if qry != ():
        mascot_name = qry[0][0]
    else:
        print "\n\n!!!!ERROR!!!! - no mascot_name for %s, %s" % (year, team_abb)
        mascot_name = None

    return mascot_name

def get_park_factors(team_abb, year):
    """"
    Scaled park factors (by a factor of 1/3) from fangraphs
    """
    qry = db.query("""SELECT park_factor
    FROM teams_current_franchise tcf
    JOIN teams t ON (tcf.team_name = t.team_name)
    WHERE 1
        AND (tcf.primary_abb = '%s' OR tcf.secondary_abb = '%s' OR tcf.tertiary_abb = '%s' OR t.team_abb = '%s')
        AND year = %s;""" % (team_abb, team_abb, team_abb, team_abb, year))
    if qry != ():
        park_factor = qry[0][0]
    else:
        print "\n\n!!!!ERROR!!!! - no park_factor for %s, %s" % (year, team_abb)
        park_factor = 100.0

    return park_factor

def get_pos_adj(position):
    qry = db.query("SELECT adjustment FROM helper_positional_adjustment WHERE position = '%s';" % (position))
    if qry != ():
        pos_adj = qry[0][0]
    else:
        print "\n\n!!!!ERROR!!!! - no position adjustment for %s" % (position)
        pos_adj = 0.0

    return pos_adj

def get_pos_formula(position):
    """
    Returns coefficients for error/range/arm/passed ball values according to http://www.ontonova.com/floodstudy/4647-5.html.
    This should possibly be scaled down?
    """
    # [range, error, arm, passed ball]

    qry = db.query("SELECT rng, err, arm, passed_ball FROM helper_zips_positions WHERE position = '%s';" % (position))
    if qry != ():
        pos_formula = [qry[0][0], qry[0][1], qry[0][2], qry[0][3]]
    else:
        print "\n\n!!!!ERROR!!!! - no position formula for %s" % (position)
        pos_formula = [0,0,0,0]

    # for i, v in enumerate(pos_formula):
    #     # research from http://dmbo.net/smf/index.php?topic=4883.0 and ad_hoc/defensive_value_analysis.xlsx shows that the original defensive values should be regressed back ~72.5%
    #     pos_formula[i] = 0.725 * v

    return pos_formula

def get_league_average_hitters(year, category):
    q = """SELECT
    pa,
    r,
    (h+bb+hbp)/pa as obp,
    (1b + 2*2b + 3*3b + 4*hr)/ab as slg,
    woba
    FROM processed_league_averages_hitting
    WHERE year = %s
    """
    qry = q % year
    query = db.query(qry)[0]
    lg_pa, lg_r, lg_obp, lg_slg, lg_woba = query
    avgs = {"lg_pa":lg_pa, "lg_r":lg_r, "lg_obp":lg_obp, "lg_slg":lg_slg, "lg_woba":lg_woba}

    return avgs.get(category)

def get_zips_average_hitters(year, category):
    q = """SELECT
    pa,
    r,
    (h+bb+hbp)/pa as obp,
    (1b + 2*2b + 3*3b + 4*hr)/ab as slg,
    woba
    FROM zips_averages_hitting
    WHERE year = %s
    """
    qry = q % year
    query = db.query(qry)[0]
    lg_pa, lg_r, lg_obp, lg_slg, lg_woba = query
    avgs = {"lg_pa":lg_pa, "lg_r":lg_r, "lg_obp":lg_obp, "lg_slg":lg_slg, "lg_woba":lg_woba}

    return avgs.get(category)

def get_offensive_metrics(year, pf, pa, ab, bb, hbp, _1b, _2b, _3b, hr, sb, cs):
    """
    Converts a players offensive boxscore stats in a given year to more advanced stats (ops, wOBA, park_adjusted wOBA, OPS+, wRC, wRC/27, wRC+, RAA, and offensive WAR)
    """
    wOBA = ((0.691*bb + 0.722*hbp + 0.884*_1b + 1.257*_2b + 1.593*_3b + 2.058*hr + 0.2*sb - 0.398*cs)/(pa))
    
    park_wOBA = wOBA/pf
    
    h = _1b + _2b + _3b + hr 
    if pa != 0:
        obp = (h + bb + hbp)/float(pa)
    else:
        obp = 0.0
    if ab != 0:
        slg = (_1b + 2*_2b + 3*_3b + 4*hr)/float(ab)
    else:
        slg = 0.0

    ops = obp+slg
    lg_obp = float(get_league_average_hitters(year,'lg_obp'))
    lg_slg = float(get_league_average_hitters(year,'lg_slg'))
    OPS_plus = 100*(((obp/pf)/lg_obp)+((slg/pf)/lg_slg)-1)

    lg_woba = float(get_league_average_hitters(year,'lg_woba'))
    lg_r = float(get_league_average_hitters(year,'lg_r'))
    lg_pa = float(get_league_average_hitters(year,'lg_pa'))
    wrc = (((park_wOBA-lg_woba)/1.15)+(lg_r/lg_pa))*pa

    if (ab-h) != 0:
        wrc27 = wrc*27/(ab-h)
    else:
        wrc27 = 0.0

    wRC_plus = ((wrc/pa/(lg_r/lg_pa)*100))

    raa = pa*((park_wOBA-lg_woba)/1.25)

    oWAR = raa/10

    return ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR

def get_zips_offensive_metrics(year, pf, pa, ab, bb, hbp, _1b, _2b, _3b, hr, sb, cs):
    """
    Converts a players offensive zips boxscore stats in a given year to more advanced stats (ops, wOBA, park_adjusted wOBA, OPS+, wRC, wRC/27, wRC+, RAA, and offensive WAR)
    """
    wOBA = ((0.691*bb + 0.722*hbp + 0.884*_1b + 1.257*_2b + 1.593*_3b + 2.058*hr + 0.2*sb - 0.398*cs)/(pa))
    
    park_wOBA = wOBA/pf
    
    h = _1b + _2b + _3b + hr 
    if pa != 0:
        obp = (h + bb + hbp)/float(pa)
    else:
        obp = 0.0
    if ab != 0:
        slg = (_1b + 2*_2b + 3*_3b + 4*hr)/float(ab)
    else:
        slg = 0.0

    ops = obp+slg
    lg_obp = float(get_zips_average_hitters(year,'lg_obp'))
    lg_slg = float(get_zips_average_hitters(year,'lg_slg'))
    OPS_plus = 100*(((obp/pf)/lg_obp)+((slg/pf)/lg_slg)-1)

    lg_woba = float(get_zips_average_hitters(year,'lg_woba'))
    lg_r = float(get_zips_average_hitters(year,'lg_r'))
    lg_pa = float(get_zips_average_hitters(year,'lg_pa'))
    wrc = (((park_wOBA-lg_woba)/1.15)+(lg_r/lg_pa))*pa

    if (ab-h) != 0:
        wrc27 = wrc*27/(ab-h)
    else:
        wrc27 = 0.0

    wRC_plus = ((wrc/pa/(lg_r/lg_pa)*100))

    raa = pa*((park_wOBA-lg_woba)/1.25)

    oWAR = raa/10

    return ops, wOBA, park_wOBA, OPS_plus, wrc, wrc27, wRC_plus, raa, oWAR

def get_league_average_pitchers(year, category):
    q = """SELECT
    r,
    gs,
    era,
    era as fip,
    fip_const
    FROM processed_league_averages_pitching
    WHERE year = %s
    """
    qry = q % year
    query = db.query(qry)[0]
    lg_r, lg_gs, lg_era, lg_fip, fip_const = query
    avgs = {"lg_r":lg_r, "lg_gs":lg_gs, "lg_era":lg_era, "lg_fip":lg_fip, "fip_const":fip_const}

    return avgs.get(category)

def get_zips_average_pitchers(year, category):
    q = """SELECT
    r,
    gs,
    era,
    era as fip,
    fip_const
    FROM zips_averages_pitching
    WHERE year = %s
    """
    qry = q % year
    query = db.query(qry)[0]
    lg_r, lg_gs, lg_era, lg_fip, fip_const = query
    avgs = {"lg_r":lg_r, "lg_gs":lg_gs, "lg_era":lg_era, "lg_fip":lg_fip, "fip_const":fip_const}

    return avgs.get(category)

def get_pitching_metrics(metric_9, ip, year, pf,  g, gs, _type):
    """
    Converts a players pitching boxscore stats in a given year to either parkadjusted FIP/ERA, FIP-/ERA-, fWAR/rWAR.
    """
    park_metric = metric_9/pf

    search_metric = 'lg_' + _type
    lg_metric = float(get_league_average_pitchers(year, search_metric))
    metric_min = 100*(park_metric/lg_metric)

    RApxMETRIC = float(park_metric)/0.92

    lg_r = float(get_league_average_pitchers(year, 'lg_r'))
    lg_gs = float(get_league_average_pitchers(year, 'lg_gs'))
    metric_RE = ((((18-(float(ip)/float(g)))*(float(lg_r)/float(lg_gs))+(float(ip)/float(g))*RApxMETRIC)/18)+2)*1.5

    if (float(gs)/float(g)) > 0.5:
        METRIC_x_win = ((lg_metric-RApxMETRIC)/(metric_RE))+0.5
        METRIC_x_win_9 = METRIC_x_win - 0.38
    else:
        METRIC_x_win = ((lg_metric-RApxMETRIC)/(metric_RE))+0.52
        METRIC_x_win_9 = METRIC_x_win - 0.46

    METRIC_WAR = METRIC_x_win_9*float(ip)/9.0

    return park_metric, metric_min, METRIC_WAR

def get_zips_pitching_metrics(metric_9, ip, year, pf,  g, gs, _type):
    park_metric = metric_9/pf

    search_metric = 'lg_' + _type
    lg_metric = float(get_zips_average_pitchers(year, search_metric))
    metric_min = 100*(park_metric/lg_metric)

    RApxMETRIC = float(park_metric)/0.92

    lg_r = float(get_zips_average_pitchers(year, 'lg_r'))
    lg_gs = float(get_zips_average_pitchers(year, 'lg_gs'))
    metric_RE = ((((18-(float(ip)/float(g)))*(float(lg_r)/float(lg_gs))+(float(ip)/float(g))*RApxMETRIC)/18)+2)*1.5

    if (gs >= 3 or float(gs)/float(g) > 0.4):
        METRIC_x_win = ((lg_metric-RApxMETRIC)/(metric_RE))+0.5
        METRIC_x_win_9 = METRIC_x_win - 0.38
    else:
        METRIC_x_win = ((lg_metric-RApxMETRIC)/(metric_RE))+0.52
        METRIC_x_win_9 = METRIC_x_win - 0.46

    METRIC_WAR = METRIC_x_win_9*float(ip)/9.0

    return park_metric, metric_min, METRIC_WAR

def get_hand(player_name):
    if player_name[len(player_name)-1:] == "*":
        hand = 'l'
    elif player_name[len(player_name)-1:] == "#":
        hand = 's'
    else:
        hand = 'r'

    return hand

def get_def_values(search_name, position, year):
    """
    Gets the baseline defensive ratings for a player given the desired position and year.
    """
    p = position.lower()
    pos = position.upper()
    rn = '%s_range' % p
    er = '%s_error' % p
    arm, pb = 0,2
    if p == 'c':
        arm = 'c_arm'
        pb = 'c_pb'
    elif p in ('lf','rf','cf'):
        arm = 'of_arm'

    try:
        if p not in ('p','dh', 'ph', 'if', 'sp', 'rp', 'of'):
            rtg_q = """SELECT
    %s,
    %s,
    %s,
    %s
    FROM zips_defense
    WHERE year = %s
    AND player_name = '%s'"""
        
            rtg_qry = rtg_q % (rn, er, arm, pb, year, search_name)
            rtgs = db.query(rtg_qry)[0]
        else:
            rtgs = (0,0,0,0)
    except IndexError:
        rtgs = (0,0,0,0)

    _r, error, _a, passed_ball = rtgs
    if error is None:
        error = 100
    if _r is None:
        _r = 'AV'
    if _a is None:
        _a = 'AV'
    if passed_ball is None:
        passed_ball = 2
    _range = str(_r)
    _arm = str(_a)

    # range and arm text values need to translate to numeric values
    if _range.upper() in ('PO','PR'):
        num_rn = -2
    elif _range.upper() in ('FR',):
        num_rn = -1
    elif _range.upper() in ('AV','AVG'):
        num_rn = 0
    elif _range.upper() in ('VG',):
        num_rn = 1
    elif _range.upper() in ('EX',):
        num_rn = 2
    else:
        num_rn = 0

    if _arm.upper() in ('PO','PR'):
        num_arm = -2
    elif _arm.upper() in ('FR',):
        num_arm = -1
    elif _arm.upper() in ('AV','AVG'):
        num_arm = 0
    elif _arm.upper() in ('VG',):
        num_arm = 1
    elif _arm.upper() in ('EX',):
        num_arm = 2
    else:
        num_arm = 0

    weights = get_pos_formula(pos)

    rn_val = float(weights[0])*num_rn
    #100 is average error rating. we want the amount above/below this number
    err_val = float(weights[1])*((100-float(error))/100)
    arm_val = float(weights[2])*num_arm
    pb_val = float(weights[3])*(2-passed_ball)

    return rn_val, err_val, arm_val, pb_val

def input_name(player_name):
    chk_val = db.query('select count(*) from name_mapper where wrong_name = "%s"' % (player_name))[0][0]

    if chk_val == 0:
        right_fname = player_name.split(" ")[0]
        right_lname = ' '.join(player_name.split(" ")[1:])
        entry = {'wrong_name': player_name, 'right_fname': right_fname, 'right_lname': right_lname}
        db.insertRowDict(entry, 'name_mapper', insertMany=False, replace=True, rid=0,debug=1)
        db.conn.commit()
        print "\t\tEntered new player %s --> '%s'+'%s'" % (player_name, right_fname, right_lname)
