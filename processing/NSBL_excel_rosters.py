import xlrd
from py_db import db
import argparse
import NSBL_helpers as helper

db = db('NSBL')

def process(curr_year):
    rosters_link = '/Users/connordog/Dropbox/Desktop_Files/Baseball/Rosters.xlsx'

    season_gp = db.query("SELECT gs FROM processed_league_averages_pitching WHERE year = %s" % (curr_year))
    if season_gp == ():
        season_gp = 0
    else:
        season_gp = float(season_gp[0][0])/2


    workbook = xlrd.open_workbook(rosters_link)

    # iterate through all team sheets
    for index in range(4, 34):
        team_name = workbook.sheet_names()[index]

        print team_name

        team_abbs, primary_abb = helper.get_team_abbs(team_name.upper())

        entries = []

        team_sheet = workbook.sheet_by_index(index)

        # get a maximum row for each sheet
        for row in range(1,100):
            if team_sheet.cell(row,1).value == 'Waived Players':
                max_row = row
                break

        position = ''
        for row in range(8,max_row):
            if team_sheet.cell(row, 1).value == 'Pitchers':
                position = 'p'
            if team_sheet.cell(row, 1).value == 'Catchers':
                position = 'c'
            if team_sheet.cell(row, 1).value == 'Infielders':
                position = 'if'
            if team_sheet.cell(row, 1).value == 'Outfielders':
                position = 'of'

            entered_name = team_sheet.cell(row, 1).value
            if position == 'c' and entered_name == 'Smith, Will':
                entered_name = 'D. Smith, Will'
            player_name, first_name, last_name = name_parser(entered_name)

            if team_sheet.cell(row, 2).value not in ('Year','') and team_sheet.cell(row, 3).value not in ('Salary', ''):

                salary = team_sheet.cell(row, 3).value
                year = team_sheet.cell(row, 2).value
                expires = team_sheet.cell(row, 4).value
                opt = team_sheet.cell(row, 5).value
                NTC = team_sheet.cell(row, 8).value
                salary_counted = team_sheet.cell(row, 9).value


                entry = {'year':curr_year, 'gp':season_gp, 'player_name':player_name, "fname":first_name, "lname":last_name, "team_abb":primary_abb,  "position":position, "salary":salary, "contract_year":year, "expires":expires, "opt":opt, "NTC":NTC, "salary_counted":salary_counted, "entered_name":entered_name}
                # print entry
                entries.append(entry)


        if entries != []: 
            db.insertRowDict(entries, 'excel_rosters', replace=True, insertMany=True, rid=0)
        db.conn.commit()


def name_parser(reverse_name):
    player_mapper = {
    "AJ Cole": ["A.J.", "Cole"],
    "AJ Minter": ["A.J.", "Minter"],
    "AJ Pollock": ["A.J.", "Pollock"],
    "Andrew Yerzy": ["Andy", "Yerzy"],
    "Anthony Siegler": ["Anthony", "Seigler"],
    "Austin Adams": ["Austin L.", "Adams"],
    "Noah Naylor": ["Bo", "Naylor"],
    "Bobby Jr Witt": ["Bobby", "Witt Jr."],
    "CJ Cron": ["C.J.", "Cron"],
    "Carl Edwards": ["Carl", "Edwards Jr."],
    "Chi-Chi Gonzalez": ["Chi Chi", "Gonzalez"],
    "Cristin Stewart": ["Christin", "Stewart"],
    "Cody (93) Reed": ["Cody", "Reed"],
    "Cody (96) Reed": ["Cody", "Reed"],
    "Colton Brewer": ["Colten", "Brewer"],
    "DJ Peterson": ["D.J.", "Peterson"],
    "DJ Stewart": ["D.J.", "Stewart"],
    "Daniel Winkler": ["Dan", "Winkler"],
    "Daulton Jeffries": ["Daulton", "Jefferies"],
    "Phelps. David": ["David", "Phelps"],
    "Delino DeShields Jr": ["Delino", "DeShields"],
    "D.J. Peters": ["DJ", "Peters"],
    "D.L. Hall": ["DL", "Hall"],
    "Duane Underwood": ["Duane", "Underwood Jr."],
    "Tatis Jr. Fernando": ["Fernando", "Tatis Jr."],
    "Franklin (97) Perez": ["Franklin", "Perez"],
    "Gregory Deichmann": ["Greg", "Deichmann"],
    "Greg Polanco": ["Gregory", "Polanco"],
    "Jackie Bradley Jr": ["Jackie", "Bradley Jr."],
    "Jake deGrom": ["Jacob", "deGrom"],
    "Jacob Petricka": ["Jake", "Petricka"],
    "Hot Jameson Taillon": ["Jameson", "Taillon"],
    "Jason Groome": ["Jay", "Groome"],
    "Ji Man Choi": ["Ji-Man", "Choi"],
    "Jordan Adell": ["Jo", "Adell"],
    'Joe "Overdraft" Palumbo': ["Joe", "Palumbo"],
    "Jonathan Gray": ["Jon", "Gray"],
    "Jonathon Schoop": ["Jonathan", "Schoop"],
    "Johnny Venters": ["Jonny", "Venters"],
    "(Jose) Vicente Campos": ["Jose", "Campos"],
    "J.T. Riddle": ["JT", "Riddle"],
    "Julio (97) Rodriguez": ["Julio", "Rodriguez"],
    "Jung-ho Kang": ["Jung Ho", "Kang"],
    "Enrique Kike Hernandez": ["Kike", "Hernandez"],
    "Lenny Torres": ["Lenny", "Torres Jr."],
    "Lourdes Jr Gurriel": ["Lourdes", "Gurriel Jr."],
    "Luke Sims": ["Lucas", "Sims"],
    "Luis Alejandro (IF) Basabe": ["Luis Alejandro", "Basabe"],
    "Luis Alexander (OF) Basabe": ["Luis Alexander", "Basabe"],
    "Luis (05/16/00) Garcia": ["Luis", "Garcia"],
    "Mathew Skole": ["Matt", "Skole"],
    "Matt Bowman": ["Matthew", "Bowman"],
    "Matt Joyce": ["Matthew", "Joyce"],
    "Michael Aguilar": ["Miguel", "Aguilar"],
    "Mitch White": ["Mitchell", "White"],
    "M.J. Melendez": ["MJ", "Melendez"],
    "Nathan Orf": ["Nate", "Orf"],
    "Nate Eovaldi": ["Nathan", "Eovaldi"],
    "Nick Castellanos": ["Nicholas", "Castellanos"],
    "Pat Corbin": ["Patrick", "Corbin"],
    "Phillip Bickford": ["Phil", "Bickford"],
    "Phillip Ervin": ["Phil", "Ervin"],
    "Dick Lovelady": ["Richard", "Lovelady"],
    "Ronnie Mauricio": ["Ronny", "Mauricio"],
    "Ryan Yarbough": ["Ryan", "Yarbrough"],
    "Ryan Harper": ["Ryne", "Harper"],
    "Samuel Tuivailala": ["Sam", "Tuivailala"],
    "Seung Hwan Oh": ["Seung-hwan", "Oh"],
    "Shane Turnbull": ["Spencer", "Turnbull"],
    "Steve Okert": ["Steven", "Okert"],
    "Szapucki Thomas": ["Thomas", "Szapucki"],
    "Thomas Eshelman": ["Tom", "Eshelman"],
    "Antonio Santillan": ["Tony", "Santillan"],
    "Trenton Grisham (Clark)": ["Trent", "Grisham"],
    "Tucupita Marcana": ["Tucupita", "Marcano"],
    "Tyler Duffy": ["Tyler", "Duffey"],
    "Tyler (97) Watson": ["Tyler", "Watson"],
    "Vince Velazquez": ["Vince", "Velasquez"],
    "Vlad Jr Guerrero": ["Vladimir", "Guerrero Jr."],
    'Willie "No Gloves" Calhoun': ["Willie", "Calhoun"],

    "Lance McCullers": ["Lance", "McCullers Jr."],
    "Rafael DePaula": ["Rafael", "de Paula"],
    "Manuel Banuelos": ["Manny", "Banuelos"],
    "Chris Devinski": ["Chris", "Devenski"],
    "Ryan Pressley": ["Ryan", "Pressly"],
    "Daniel Poncedeleon": ["Daniel", "Ponce de Leon"],
    "Steven Souza": ["Steven", "Souza Jr."],
    "Zach Granite": ["Zack", "Granite"],
    "JD Martinez": ["J.D.", "Martinez"],
    "Albert Almora Jr.": ["Albert", "Almora Jr."],
    "Matthew Joyce": ["Matt", "Joyce"],
    "Mike Yazstremski": ["Mike", "Yastrzemski"],
    "Cory Dickerson": ["Corey", "Dickerson"],
    "Pete O'Brien": ["Peter", "O'Brien"],
    "Starlin Marte": ["Starling", "Marte"],
    "JT Riddle": ["J.T.", "Riddle"],
    "Giovanny Urshela": ["Gio", "Urshela"],
    "Dan Vogelbach": ["Daniel", "Vogelbach"],
    "Peter Alonso": ["Pete", "Alonso"],
    "Matt Beatty": ["Matt", "Beaty"],
    "Jose Ozuna": ["Jose", "Osuna"],
    "Matt Duffy": ["Matt", "M. Duffy"],
    "Richie Martin": ["Richie", "Martin Jr."],
    "Travis d'Arnoud": ["Travis", "d'Arnaud"],
    "K.J. Harrison": ["KJ", "Harrison"],
    "Dominic Nunez": ["Dom", "Nunez"],
    "Abraham Toro-Hernandez": ["Abraham", "Toro"],
    }

    first_name = reverse_name.split(', ')[1:]
    last_name = reverse_name.split(', ')[0]
    player_name = ' '.join(reversed(reverse_name.split(', ')))

    if player_name in player_mapper:
        first_name, last_name = player_mapper.get(player_name)
        player_name = first_name + ' ' + last_name
    return player_name, first_name, last_name

if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2020)

    args = parser.parse_args()
    
    process(args.year)