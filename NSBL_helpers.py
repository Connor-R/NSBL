# A set of helper functions for the NSBL codebase
from py_db import db
db = db('NSBL')



def get_team_abb(team_name):
    team_abb_dict = {
    "Baltimore Orioles": "Bal",
    "Boston Red Sox": "Bos",
    "New York Yankees": "NYA",
    "Tampa Bay Rays": "Tam",
    "Toronto Blue Jays": "Tor",
    "Chicago White Sox": "ChA",
    "Cleveland Indians": "Cle",
    "Detroit Tigers": "Det",
    "Kansas City Royals": "KC",
    "Minnesota Twins": "Min",
    "Houston Astros": "Hou",
    "Los Angeles Angels of Anaheim": "LAA",
    "Los Angeles Angels": "LAA",
    "Oakland Athletics": "Oak",
    "Seattle Mariners": "Sea",
    "Texas Rangers": "Tex",
    "Atlanta Braves": "Atl",
    "Miami Marlins": "Mia",
    "New York Mets": "NYN",
    "Philadelphia Phillies": "Phi",
    "Washington Nationals": "Was",
    "Chicago Cubs": "ChN",
    "Cincinnati Reds": "Cin",
    "Milwaukee Brewers": "Mil",
    "Pittsburgh Pirates": "Pit",
    "St. Louis Cardinals": "StL",
    "Arizona Diamondbacks": "Ari",
    "Colorado Rockies": "Col",
    "Los Angeles Dodgers": "LAN",
    "San Diego Padres": "SD",
    "San Francisco Giants": "SF",
    "Florida Marlins": "Mia",
    "World Champion Cardinals": "STL"
    }

    team_abb = team_abb_dict.get(team_name)

    return team_abb


def get_team_name(city_name):
    team_names_dict = {
    "Baltimore": "Baltimore Orioles",
    "Tampa Bay": "Tampa Bay Rays",
    "New York (A)": "New York Yankees",
    "Toronto": "Toronto Blue Jays",
    "Boston": "Boston Red Sox",
    "Minnesota": "Minnesota Twins",
    "Detroit": "Detroit Tigers",
    "Chicago (A)": "Chicago White Sox",
    "Cleveland": "Cleveland Indians",
    "Kansas City": "Kansas City Royals",
    "Seattle": "Seattle Mariners",
    "Texas": "Texas Rangers",
    "Oakland": "Oakland Athletics",
    "Los Angeles (A)": "Los Angeles Angels",
    "Houston": "Houston Astros",
    "New York (N)": "New York Mets",
    "Miami": "Miami Marlins",
    "Atlanta": "Atlanta Braves",
    "Washington": "Washington Nationals",
    "Philadelphia": "Philadelphia Phillies",
    "Pittsburgh": "Pittsburgh Pirates",
    "Cincinnati": "Cincinnati Reds",
    "St. Louis": "St. Louis Cardinals",
    "Chicago (N)": "Chicago Cubs",
    "Milwaukee": "Milwaukee Brewers",
    "Colorado": "Colorado Rockies",
    "San Diego": "San Diego Padres",
    "Los Angeles (N)": "Los Angeles Dodgers",
    "San Francisco": "San Francisco Giants",
    "Arizona": "Arizona Diamondbacks",
    }

    team_name = team_names_dict.get(city_name)

    return team_name

def get_mascot_names(team_abb):
    mascot_names_dict = {
    "ANA": "Angels",
    "ARI": "Diamondbacks",
    "ATL": "Braves",
    "AZ": "Diamondbacks",
    "AZD": "Diamondbacks",
    "BAL": "Orioles",
    "BOS": "Red Sox",
    "CHA": "White Sox",
    "CHC": "Cubs",
    "CHN": "Cubs",
    "CIN": "Reds",
    "CLE": "Indians",
    "CLV": "Indians",
    "COL": "Rockies",
    "CWS": "White Sox",
    "DET": "Tigers",
    "FLA": "Marlins",
    "FLO": "Marlins",
    "HOU": "Astros",
    "KC": "Royals",
    "KCR": "Royals",
    "LA": "Dodgers",
    "LAA": "Angels",
    "LAD": "Dodgers",
    "LAN": "Dodgers",
    "MIA": "Marlins",
    "MIL": "Brewers",
    "MIN": "Twins",
    "NYA": "Yankees",
    "NYM": "Mets",
    "NYN": "Mets",
    "NYY": "Yankees",
    "OAK": "Athletics",
    "PHI": "Phillies",
    "PIT": "Pirates",
    "SD": "Padres",
    "SDP": "Padres",
    "SEA": "Mariners",
    "SF": "Giants",
    "SFG": "Giants",
    "STL": "Cardinals",
    "TAM": "Rays",
    "TB": "Rays",
    "TBR": "Rays",
    "TEX": "Rangers",
    "TOR": "Blue Jays",
    "WAS": "Nationals"
    }

    mascot_name = mascot_names_dict.get(team_abb)

    return mascot_name


def get_team_abbs(team_name):
    team_abbreviations =[
    {"ANGELS":("ANA", "LAA", "", "")},
    {"ASTROS":("HOU", "", "", "")},
    {"ATHLETICS":("OAK", "", "", "")},
    {"BLUE JAYS":("TOR", "", "", "")},
    {"BLUEJAYS":("TOR", "", "", "")},
    {"BRAVES":("ATL", "", "", "")},
    {"BREWERS":("MIL", "", "", "")},
    {"CARDINALS":("STL", "", "", "")},
    {"CUBS":("CHC", "CHN", "", "")},
    {"DIAMONDBACKS":("ARI", "AZ", "AZD", "")},
    {"DODGERS":("LA", "LAD", "LAN", "")},
    {"GIANTS":("SF", "SFG", "", "")},
    {"INDIANS":("CLE", "CLV", "", "")},
    {"MARINERS":("SEA", "", "", "")},
    {"MARLINS":("FLA", "FLO", "MIA", "")},
    {"METS":("NYM", "NYN", "", "")},
    {"NATIONALS":("WAN", "WAS", "", "")},
    {"ORIOLES":("BAL", "BALT", "", "")},
    {"PADRES":("SAN", "SD", "SDP", "")},
    {"PHILLIES":("PHI", "", "", "")},
    {"PIRATES":("PIT", "", "", "")},
    {"RANGERS":("TEX", "", "", "")},
    {"RAYS":("TAM", "TB", "TBA", "TBR")},
    {"RED SOX":("BOS", "", "", "")},
    {"REDSOX":("BOS", "", "", "")},
    {"REDS":("CIN", "", "", "")},
    {"ROCKIES":("COL", "", "", "")},
    {"ROYALS":("KC", "KCR", "", "")},
    {"TIGERS":("DET", "", "", "")},
    {"TWINS":("MIN", "", "", "")},
    {"WHITE SOX":("CHA", "CHW", "CWS", "")},
    {"WHITESOX":("CHA", "CHW", "CWS", "")},
    {"YANKEES":("NYA", "NYY", "", "")}
    ]

    team_abbs = []
    for i in team_abbreviations:
        if i.keys()[0] == team_name.upper():
            team_abbs = i.get(team_name.upper())
    primary_abb = team_abbs[0]

    return team_abbs, primary_abb


def get_park_factors(team_abb):
    park_factors_dict = {
    "ANA":98.33,
    "LAA":98.33,
    "HOU":98.33,
    "OAK":100,
    "TOR":99,
    "ATL":99.67,
    "MIL":101,
    "STL":99.33,
    "CHC":100.67,
    "CHN":100.67,
    "ARI":101.33,
    "AZ":101.33,
    "AZD":101.33,
    "LA":98.67,
    "LAD":98.67,
    "LAN":98.67,
    "SF":97.67,
    "SFG":97.67,
    "CLE":99,
    "CLV":99,
    "SEA":99,
    "FLA":100.33,
    "FLO":100.33,
    "MIA":100.33,
    "NYM":98.33,
    "NYN":98.33,
    "WAN":100,
    "WAS":100,
    "BAL":100.67,
    "BALT":100.67,
    "SAN":98,
    "SD":98,
    "SDP":98,
    "PHI":100,
    "PIT":99,
    "TEX":102,
    "TAM":98.33,
    "TB":98.33,
    "TBA":98.33,
    "TBR":98.33,
    "BOS":101.33,
    "CIN":100.33,
    "COL":105.67,
    "KC":100.33,
    "KCR":100.33,
    "DET":100.67,
    "MIN":100.33,
    "CHA":101.33,
    "CHW":101.33,
    "CWS":101.33,
    "NYA":101,
    "NYY":101,
    "NONE":100,
    "":100,
    }

    park_factor = park_factors_dict.get(team_abb)

    return park_factor



def get_pos_adj(position):
    pos_adj_dict = {
    "P":60.0,
    "C":12.5,
    "1B":-12.5,
    "2B":2.5,
    "3B":2.5,
    "SS":7.5,
    "LF":-7.5,
    "CF":2.5,
    "RF":-7.5,
    "DH":-17.5,
    "PH":-17.5,
    "IF":2.5,
    "":0
    }

    pos_adj = pos_adj_dict.get(position)

    return pos_adj


def get_pos_formula(position):
    # [range, error, arm, passed ball]
    pos_formula_dict = {
    "P":[0.0,0.0,0.0,0.0],
    "C":[2.0,0.0,2.33,1.0],
    "1B":[9.46,7.78,0.0,0.0],
    "2B":[7.92,14.06,0.0,0.0],
    "3B":[15.25,14.22,0.0,0.0],
    "SS":[6.83,19.61,0.0,0.0],
    "LF":[15.46,5.94,5.17,0.0],
    "CF":[15.46,6.39,8.0,0.0],
    "RF":[15.75,6.44,6.83,0.0],
    "DH":[0.0,0.0,0.0,0.0]
    }

    pos_formula = pos_formula_dict.get(position)

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


def get_offensive_metrics(year, pf, pa, ab, bb, hbp, _1b, _2b, _3b, hr, sb, cs):
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


def get_pitching_metrics(metric_9, ip, year, pf,  g, gs, _type):
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


def get_hand(player_name):
    if player_name[len(player_name)-1:] == "*":
        hand = 'l'
    elif player_name[len(player_name)-1:] == "#":
        hand = 's'
    else:
        hand = 'r'

    return hand



def get_def_values(search_name, position, year):
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
        if p not in ('p','dh'):
            rtg_q = """SELECT
%s,
%s,
%s,
%s
FROM zips_defense_%s
WHERE player_name = '%s'"""
        
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

    rn_val = weights[0]*num_rn
    #100 is average error rating. we want the amount above/below this number
    err_val = weights[1]*((100-float(error))/100)
    arm_val = weights[2]*num_arm
    pb_val = weights[3]*(2-passed_ball)

    return rn_val, err_val, arm_val, pb_val