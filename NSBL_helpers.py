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

def get_team_abb2(team_name):
    team_abb_dict = {
    "2006Anaheim Angels": "ANA",
    "2009Anaheim Angels": "ANA",
    "2007Arizona Diamondbacks": "Ari",
    "2009Arizona Diamondbacks": "ARI",
    "2010Arizona Diamondbacks": "ARI",
    "2011Arizona Diamondbacks": "Ari",
    "2012Arizona Diamondbacks": "Ari",
    "2013Arizona Diamondbacks": "Ari",
    "2014Arizona Diamondbacks": "Ari",
    "2015Arizona Diamondbacks": "Ari",
    "2016Arizona Diamondbacks": "Ari",
    "2017Arizona Diamondbacks": "Ari",
    "2006Atlanta Braves": "ATL",
    "2007Atlanta Braves": "Atl",
    "2008Atlanta Braves": "ATL",
    "2009Atlanta Braves": "ATL",
    "2010Atlanta Braves": "ATL",
    "2011Atlanta Braves": "Atl",
    "2012Atlanta Braves": "Atl",
    "2013Atlanta Braves": "Atl",
    "2014Atlanta Braves": "Atl",
    "2015Atlanta Braves": "Atl",
    "2016Atlanta Braves": "Atl",
    "2017Atlanta Braves": "Atl",
    "2006Arizona Diamondbacks": "AZ",
    "2008Arizona Diamondbacks": "AZD",
    "2006Baltimore Orioles": "BAL",
    "2007Baltimore Orioles": "Bal",
    "2008Baltimore Orioles": "BAL",
    "2009Baltimore Orioles": "BAL",
    "2010Baltimore Orioles": "BAL",
    "2011Baltimore Orioles": "Bal",
    "2012Baltimore Orioles": "Bal",
    "2013Baltimore Orioles": "Bal",
    "2014Baltimore Orioles": "Bal",
    "2015Baltimore Orioles": "Bal",
    "2016Baltimore Orioles": "Bal",
    "2017Baltimore Orioles": "Bal",
    "2006Boston Red Sox": "BOS",
    "2007Boston Red Sox": "Bos",
    "2008Boston Red Sox": "BOS",
    "2009Boston Red Sox": "BOS",
    "2010Boston Red Sox": "BOS",
    "2011Boston Red Sox": "Bos",
    "2012Boston Red Sox": "Bos",
    "2013Boston Red Sox": "Bos",
    "2014Boston Red Sox": "Bos",
    "2015Boston Red Sox": "Bos",
    "2016Boston Red Sox": "Bos",
    "2017Boston Red Sox": "Bos",
    "2007Chicago White Sox": "ChA",
    "2009Chicago White Sox": "CHA",
    "2010Chicago White Sox": "CHA",
    "2011Chicago White Sox": "ChA",
    "2012Chicago White Sox": "ChA",
    "2013Chicago White Sox": "ChA",
    "2014Chicago White Sox": "ChA",
    "2015Chicago White Sox": "ChA",
    "2016Chicago White Sox": "ChA",
    "2017Chicago White Sox": "ChA",
    "2006Chicago Cubs": "CHC",
    "2008Chicago Cubs": "CHC",
    "2007Chicago Cubs": "ChN",
    "2009Chicago Cubs": "CHN",
    "2010Chicago Cubs": "CHN",
    "2011Chicago Cubs": "ChN",
    "2012Chicago Cubs": "ChN",
    "2013Chicago Cubs": "ChN",
    "2014Chicago Cubs": "ChN",
    "2015Chicago Cubs": "ChN",
    "2016Chicago Cubs": "ChN",
    "2017Chicago Cubs": "ChN",
    "2006Cincinnati Reds": "CIN",
    "2007Cincinnati Reds": "Cin",
    "2008Cincinnati Reds": "CIN",
    "2009Cincinnati Reds": "CIN",
    "2010Cincinnati Reds": "CIN",
    "2011Cincinnati Reds": "Cin",
    "2012Cincinnati Reds": "Cin",
    "2013Cincinnati Reds": "Cin",
    "2014Cincinnati Reds": "Cin",
    "2015Cincinnati Reds": "Cin",
    "2016Cincinnati Reds": "Cin",
    "2017Cincinnati Reds": "Cin",
    "2007Cleveland Indians": "Cle",
    "2009Cleveland Indians": "CLE",
    "2010Cleveland Indians": "CLE",
    "2011Cleveland Indians": "Cle",
    "2012Cleveland Indians": "Cle",
    "2013Cleveland Indians": "Cle",
    "2014Cleveland Indians": "Cle",
    "2015Cleveland Indians": "Cle",
    "2016Cleveland Indians": "Cle",
    "2017Cleveland Indians": "Cle",
    "2006Cleveland Indians": "CLV",
    "2008Cleveland Indians": "CLV",
    "2006Colorado Rockies": "COL",
    "2007Colorado Rockies": "Col",
    "2008Colorado Rockies": "COL",
    "2009Colorado Rockies": "COL",
    "2010Colorado Rockies": "COL",
    "2011Colorado Rockies": "Col",
    "2012Colorado Rockies": "Col",
    "2013Colorado Rockies": "Col",
    "2014Colorado Rockies": "Col",
    "2015Colorado Rockies": "Col",
    "2016Colorado Rockies": "Col",
    "2017Colorado Rockies": "Col",
    "2006Chicago White Sox": "CWS",
    "2008Chicago White Sox": "CWS",
    "2006Detroit Tigers": "DET",
    "2007Detroit Tigers": "Det",
    "2008Detroit Tigers": "DET",
    "2009Detroit Tigers": "DET",
    "2010Detroit Tigers": "DET",
    "2011Detroit Tigers": "Det",
    "2012Detroit Tigers": "Det",
    "2013Detroit Tigers": "Det",
    "2014Detroit Tigers": "Det",
    "2015Detroit Tigers": "Det",
    "2016Detroit Tigers": "Det",
    "2017Detroit Tigers": "Det",
    "2006Florida Marlins": "FLA",
    "2008Florida Marlins": "FLA",
    "2009Florida Marlins": "FLA",
    "2010Florida Marlins": "FLA",
    "2007Florida Marlins": "Flo",
    "2011Florida Marlins": "Flo",
    "2006Houston Astros": "HOU",
    "2007Houston Astros": "Hou",
    "2008Houston Astros": "HOU",
    "2009Houston Astros": "HOU",
    "2010Houston Astros": "HOU",
    "2011Houston Astros": "Hou",
    "2012Houston Astros": "Hou",
    "2013Houston Astros": "Hou",
    "2014Houston Astros": "Hou",
    "2015Houston Astros": "Hou",
    "2016Houston Astros": "Hou",
    "2017Houston Astros": "Hou",
    "2006Kansas City Royals": "KC",
    "2007Kansas City Royals": "KC",
    "2009Kansas City Royals": "KC",
    "2010Kansas City Royals": "KC",
    "2011Kansas City Royals": "KC",
    "2012Kansas City Royals": "KC",
    "2013Kansas City Royals": "KC",
    "2014Kansas City Royals": "KC",
    "2015Kansas City Royals": "KC",
    "2016Kansas City Royals": "KC",
    "2017Kansas City Royals": "KC",
    "2008Kansas City Royals": "KCR",
    "2006Los Angeles Dodgers": "LA",
    "2007Los Angeles Angels": "LAA",
    "2008Los Angeles Angels": "LAA",
    "2010Los Angeles Angels": "LAA",
    "2011Los Angeles Angels": "LAA",
    "2012Los Angeles Angels": "LAA",
    "2013Los Angeles Angels": "LAA",
    "2014Los Angeles Angels": "LAA",
    "2015Los Angeles Angels": "LAA",
    "2016Los Angeles Angels": "LAA",
    "2017Los Angeles Angels": "LAA",
    "2008Los Angeles Dodgers": "LAD",
    "2009Los Angeles Dodgers": "LAD",
    "2010Los Angeles Dodgers": "LAD",
    "2007Los Angeles Dodgers": "LAN",
    "2011Los Angeles Dodgers": "LAN",
    "2012Los Angeles Dodgers": "LAN",
    "2013Los Angeles Dodgers": "LAN",
    "2014Los Angeles Dodgers": "LAN",
    "2015Los Angeles Dodgers": "LAN",
    "2016Los Angeles Dodgers": "LAN",
    "2017Los Angeles Dodgers": "LAN",
    "2012Miami Marlins": "Mia",
    "2013Miami Marlins": "Mia",
    "2014Miami Marlins": "Mia",
    "2015Miami Marlins": "Mia",
    "2016Miami Marlins": "Mia",
    "2017Miami Marlins": "Mia",
    "2006Milwaukee Brewers": "MIL",
    "2007Milwaukee Brewers": "Mil",
    "2008Milwaukee Brewers": "MIL",
    "2009Milwaukee Brewers": "MIL",
    "2010Milwaukee Brewers": "MIL",
    "2011Milwaukee Brewers": "Mil",
    "2012Milwaukee Brewers": "Mil",
    "2013Milwaukee Brewers": "Mil",
    "2014Milwaukee Brewers": "Mil",
    "2015Milwaukee Brewers": "Mil",
    "2016Milwaukee Brewers": "Mil",
    "2017Milwaukee Brewers": "Mil",
    "2006Minnesota Twins": "MIN",
    "2007Minnesota Twins": "Min",
    "2008Minnesota Twins": "MIN",
    "2009Minnesota Twins": "MIN",
    "2010Minnesota Twins": "MIN",
    "2011Minnesota Twins": "Min",
    "2012Minnesota Twins": "Min",
    "2013Minnesota Twins": "Min",
    "2014Minnesota Twins": "Min",
    "2015Minnesota Twins": "Min",
    "2016Minnesota Twins": "Min",
    "2017Minnesota Twins": "Min",
    "2007New York Yankees": "NYA",
    "2009New York Yankees": "NYA",
    "2010New York Yankees": "NYA",
    "2011New York Yankees": "NYA",
    "2012New York Yankees": "NYA",
    "2013New York Yankees": "NYA",
    "2014New York Yankees": "NYA",
    "2015New York Yankees": "NYA",
    "2016New York Yankees": "NYA",
    "2017New York Yankees": "NYA",
    "2006New York Mets": "NYM",
    "2008New York Mets": "NYM",
    "2007New York Mets": "NYN",
    "2009New York Mets": "NYN",
    "2010New York Mets": "NYN",
    "2011New York Mets": "NYN",
    "2012New York Mets": "NYN",
    "2013New York Mets": "NYN",
    "2014New York Mets": "NYN",
    "2015New York Mets": "NYN",
    "2016New York Mets": "NYN",
    "2017New York Mets": "NYN",
    "2006New York Yankees": "NYY",
    "2008New York Yankees": "NYY",
    "2006Oakland Athletics": "OAK",
    "2007Oakland Athletics": "Oak",
    "2008Oakland Athletics": "OAK",
    "2009Oakland Athletics": "OAK",
    "2010Oakland Athletics": "OAK",
    "2011Oakland Athletics": "Oak",
    "2012Oakland Athletics": "Oak",
    "2013Oakland Athletics": "Oak",
    "2014Oakland Athletics": "Oak",
    "2015Oakland Athletics": "Oak",
    "2016Oakland Athletics": "Oak",
    "2017Oakland Athletics": "Oak",
    "2006Philadelphia Phillies": "PHI",
    "2007Philadelphia Phillies": "Phi",
    "2008Philadelphia Phillies": "PHI",
    "2009Philadelphia Phillies": "PHI",
    "2010Philadelphia Phillies": "PHI",
    "2011Philadelphia Phillies": "Phi",
    "2012Philadelphia Phillies": "Phi",
    "2013Philadelphia Phillies": "Phi",
    "2014Philadelphia Phillies": "Phi",
    "2015Philadelphia Phillies": "Phi",
    "2016Philadelphia Phillies": "Phi",
    "2017Philadelphia Phillies": "Phi",
    "2006Pittsburgh Pirates": "PIT",
    "2007Pittsburgh Pirates": "Pit",
    "2008Pittsburgh Pirates": "PIT",
    "2009Pittsburgh Pirates": "PIT",
    "2010Pittsburgh Pirates": "PIT",
    "2011Pittsburgh Pirates": "Pit",
    "2012Pittsburgh Pirates": "Pit",
    "2013Pittsburgh Pirates": "Pit",
    "2014Pittsburgh Pirates": "Pit",
    "2015Pittsburgh Pirates": "Pit",
    "2016Pittsburgh Pirates": "Pit",
    "2017Pittsburgh Pirates": "Pit",
    "2006San Diego Padres": "SD",
    "2007San Diego Padres": "SD",
    "2009San Diego Padres": "SD",
    "2010San Diego Padres": "SD",
    "2011San Diego Padres": "SD",
    "2012San Diego Padres": "SD",
    "2013San Diego Padres": "SD",
    "2014San Diego Padres": "SD",
    "2015San Diego Padres": "SD",
    "2016San Diego Padres": "SD",
    "2017San Diego Padres": "SD",
    "2008San Diego Padres": "SDP",
    "2006Seattle Mariners": "SEA",
    "2007Seattle Mariners": "Sea",
    "2008Seattle Mariners": "SEA",
    "2009Seattle Mariners": "SEA",
    "2010Seattle Mariners": "SEA",
    "2011Seattle Mariners": "Sea",
    "2012Seattle Mariners": "Sea",
    "2013Seattle Mariners": "Sea",
    "2014Seattle Mariners": "Sea",
    "2015Seattle Mariners": "Sea",
    "2016Seattle Mariners": "Sea",
    "2017Seattle Mariners": "Sea",
    "2006San Francisco Giants": "SF",
    "2007San Francisco Giants": "SF",
    "2009San Francisco Giants": "SF",
    "2010San Francisco Giants": "SF",
    "2011San Francisco Giants": "SF",
    "2012San Francisco Giants": "SF",
    "2013San Francisco Giants": "SF",
    "2014San Francisco Giants": "SF",
    "2015San Francisco Giants": "SF",
    "2016San Francisco Giants": "SF",
    "2017San Francisco Giants": "SF",
    "2008San Francisco Giants": "SFG",
    "2006St. Louis Cardinals": "STL",
    "2007St. Louis Cardinals": "StL",
    "2008St. Louis Cardinals": "STL",
    "2009St. Louis Cardinals": "STL",
    "2010St. Louis Cardinals": "STL",
    "2011St. Louis Cardinals": "StL",
    "2012St. Louis Cardinals": "StL",
    "2013St. Louis Cardinals": "StL",
    "2014St. Louis Cardinals": "StL",
    "2015St. Louis Cardinals": "StL",
    "2016St. Louis Cardinals": "StL",
    "2017St. Louis Cardinals": "StL",
    "2007Tampa Bay Rays": "Tam",
    "2011Tampa Bay Rays": "Tam",
    "2012Tampa Bay Rays": "Tam",
    "2013Tampa Bay Rays": "Tam",
    "2014Tampa Bay Rays": "Tam",
    "2015Tampa Bay Rays": "Tam",
    "2016Tampa Bay Rays": "Tam",
    "2017Tampa Bay Rays": "Tam",
    "2006Tampa Bay Rays": "TB",
    "2009Tampa Bay Rays": "TB",
    "2010Tampa Bay Rays": "TB",
    "2008Tampa Bay Rays": "TBR",
    "2006Texas Rangers": "TEX",
    "2007Texas Rangers": "Tex",
    "2008Texas Rangers": "TEX",
    "2009Texas Rangers": "TEX",
    "2010Texas Rangers": "TEX",
    "2011Texas Rangers": "Tex",
    "2012Texas Rangers": "Tex",
    "2013Texas Rangers": "Tex",
    "2014Texas Rangers": "Tex",
    "2015Texas Rangers": "Tex",
    "2016Texas Rangers": "Tex",
    "2017Texas Rangers": "Tex",
    "2006Toronto Blue Jays": "TOR",
    "2007Toronto Blue Jays": "Tor",
    "2008Toronto Blue Jays": "TOR",
    "2009Toronto Blue Jays": "TOR",
    "2010Toronto Blue Jays": "TOR",
    "2011Toronto Blue Jays": "Tor",
    "2012Toronto Blue Jays": "Tor",
    "2013Toronto Blue Jays": "Tor",
    "2014Toronto Blue Jays": "Tor",
    "2015Toronto Blue Jays": "Tor",
    "2016Toronto Blue Jays": "Tor",
    "2017Toronto Blue Jays": "Tor",
    "2006Washington Nationals": "WAS",
    "2007Washington Nationals": "Was",
    "2008Washington Nationals": "WAS",
    "2009Washington Nationals": "WAS",
    "2010Washington Nationals": "WAS",
    "2011Washington Nationals": "Was",
    "2012Washington Nationals": "Was",
    "2013Washington Nationals": "Was",
    "2014Washington Nationals": "Was",
    "2015Washington Nationals": "Was",
    "2016Washington Nationals": "Was",
    "2017Washington Nationals": "Was",
    }

    team_abb = team_abb_dict.get(team_name)

    return team_abb

def get_division(team_name):

    division_dict = {
    "Arizona Diamondbacks": "NL West",
    "Atlanta Braves": "NL East",
    "Baltimore Orioles": "AL East",
    "Boston Red Sox": "AL East",
    "Chicago Cubs": "NL Central",
    "Chicago White Sox": "AL Central",
    "Cincinnati Reds": "NL Central",
    "Cleveland Indians": "AL Central",
    "Colorado Rockies": "NL West",
    "Detroit Tigers": "AL Central",
    "Houston Astros": "AL West",
    "Kansas City Royals": "AL Central",
    "Los Angeles Angels": "AL West",
    "Los Angeles Dodgers": "NL West",
    "Miami Marlins": "NL East",
    "Milwaukee Brewers": "NL Central",
    "Minnesota Twins": "AL Central",
    "New York Mets": "NL East",
    "New York Yankees": "AL East",
    "Oakland Athletics": "AL West",
    "Philadelphia Phillies": "NL East",
    "Pittsburgh Pirates": "NL Central",
    "San Diego Padres": "NL West",
    "San Francisco Giants": "NL West",
    "Seattle Mariners": "AL West",
    "St. Louis Cardinals": "NL Central",
    "Tampa Bay Rays": "AL East",
    "Texas Rangers": "AL West",
    "Toronto Blue Jays": "AL East",
    "Washington Nationals": "NL East"
    }

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
    {"ANGELS":("LAA", "ANA", "", "")},
    {"ASTROS":("HOU", "", "", "")},
    {"ATHLETICS":("OAK", "", "", "")},
    {"BLUE JAYS":("TOR", "", "", "")},
    {"BLUEJAYS":("TOR", "", "", "")},
    {"BRAVES":("ATL", "", "", "")},
    {"BREWERS":("MIL", "", "", "")},
    {"CARDINALS":("STL", "", "", "")},
    {"CUBS":("CHC", "CHN", "", "")},
    {"DIAMONDBACKS":("ARI", "AZ", "AZD", "")},
    {"DODGERS":("LAN", "LAD", "LA", "")},
    {"GIANTS":("SF", "SFG", "", "")},
    {"INDIANS":("CLE", "CLV", "", "")},
    {"MARINERS":("SEA", "", "", "")},
    {"MARLINS":("MIA", "FLO", "FLA", "")},
    {"METS":("NYM", "NYN", "", "")},
    {"NATIONALS":("WAS", "WAN", "", "")},
    {"ORIOLES":("BAL", "BALT", "", "")},
    {"PADRES":("SD", "SAN", "SDP", "")},
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

    rn_val = weights[0]*num_rn
    #100 is average error rating. we want the amount above/below this number
    err_val = weights[1]*((100-float(error))/100)
    arm_val = weights[2]*num_arm
    pb_val = weights[3]*(2-passed_ball)

    return rn_val, err_val, arm_val, pb_val