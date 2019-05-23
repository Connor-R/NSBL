import xlrd
from py_db import db
import argparse
import NSBL_helpers as helper

db = db('NSBL')

def process(curr_year):
    rosters_link = '/Users/connordog/Dropbox/Desktop_Files/Baseball/Rosters.xls'

    #Each time we run this, we clear the pre-existing table
    db.query("TRUNCATE TABLE `current_rosters_excel`")

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

            reverse_name = team_sheet.cell(row, 1).value
            player_name = name_parser(reverse_name)

            if team_sheet.cell(row, 2).value not in ('Year','') and team_sheet.cell(row, 3).value not in ('Salary', ''):

                salary = team_sheet.cell(row, 3).value
                year = team_sheet.cell(row, 2).value
                expires = team_sheet.cell(row, 4).value
                opt = team_sheet.cell(row, 5).value
                NTC = team_sheet.cell(row, 8).value
                salary_counted = team_sheet.cell(row, 9).value


                entry = {'player_name':player_name, "team_abb":primary_abb,  "position":position, "salary":salary, "year":year, "expires":expires, "opt":opt, "NTC":NTC, "salary_counted":salary_counted}
                entries.append(entry)


        if entries != []: 
            db.insertRowDict(entries, 'current_rosters_excel', replace=True, insertMany=True, rid=0)
        db.conn.commit()


def name_parser(reverse_name):
    player_mapper = {
    'Willie "No Gloves" Calhoun':"Willie Calhoun",
    'Willie "The Butcher" Calhoun':"Willie Calhoun",
    "(Jose) Vicente Campos":"Jose Campos",
    "Adam Brett Walker":"Adam Brett Walker II",
    "Adam C. Eaton":"Adam Eaton",
    "AJ Cole":"A.J. Cole",
    "AJ Minter":"A.J. Minter",
    "AJ Pollock":"A.J. Pollock",
    "AJ Ramos":"A.J. Ramos",
    "AJ Reed":"A.J. Reed",
    "Andrew Yerzy":"Andy Yerzy",
    "Antonio Santillan":"Tony Santillan",
    "Chi Chi Gonzalez":"Alex Gonzalez",
    "Chris (86) Carter":"Chris Carter",
    "Chris Young":"Chris B. Young",
    "CJ Cron":"C.J. Cron",
    "Cody (93) Reed":"Cody Reed",
    "Cody (96) Reed":"Cody Reed",
    "Cristin Stewart":"Christin Stewart",
    "D.J. Peters":"DJ Peters",
    "D.L. Hall":"DL Hall",
    "Dante Bichette Jr":"Dante Bichette Jr.",
    "Daulton Jeffries":"Daulton Jefferies",
    "DJ Davis":"D.J. Davis",
    "DJ Peterson":"D.J. Peterson",
    "DJ Stewart":"D.J. Stewart",
    "Francellis Montas":"Frankie Montas",
    "Franklin (97) Perez":"Franklin Perez",
    "Greg Bird":"Gregory Bird",
    "Greg Polanco":"Gregory Polanco",
    "Hudson Potts (Sanchez)":"Hudson Potts",
    "Isaiah (Zeke) White":"Zeke White",
    "Jackie Bradley Jr":"Jackie Bradley Jr.",
    "James Taillon":"Jameson Taillon",
    "Jason Groome":"Jay Groome",
    "JJ Hardy":"J.J. Hardy",
    "Jonathan Singleton":"Jon Singleton",
    "Jonathon Schoop":"Jonathan Schoop",
    "Jung-ho Kang":"Jung Ho Kang",
    """Kevin "Fly Fatass Fly" Smith""":"Kevin Smith",
    "Lenny Torres":"Lenny Torres Jr.",
    "Luis Alejandro (IF) Basabe":"Luis Alejandro Basabe",
    "Luis Alexander (OF) Basabe":"Luis Alexander Basabe",
    "Luke Sims":"Lucas Sims",
    "M.J. Melendez":"MJ Melendez",
    "Matt Joyce":"Matthew Joyce",
    "Matt M (91) Duffy":"Matt M. Duffy",
    "Michael Trout":"Mike Trout",
    "Mitch White":"Mitchell White",
    "Ozhaino Albies":"Ozzie Albies",
    "Phillip Ervin":"Phil Ervin",
    "Raul A. Mondesi":"Raul Adalberto Mondesi",
    "Steven Pearce":"Steve Pearce",
    "Steven Souza Jr.":"Steven Souza",
    "Steven Souza Jr":"Steven Souza",
    "Szapucki Thomas":"Thomas Szapucki",
    "Tatis Jr. Fernando":"Fernando Tatis Jr.",
    "Thomas Eshelman":"Tom Eshelman",
    "Trenton Grisham (Clark)":"Trent Grisham",
    "Tyler (97) Watson":"Tyler Watson",
    "Vlad Jr Guerrero":"Vladimir Guerrero Jr.",
    "Melvin Jr Upton":"Melvin Upton Jr.",
    "Ass-Dribble Cabrera": "Asdrubal Cabrera",
    "Austin Adams": "Austin L. Adams",
    "Carl Edwards": "Carl Edwards Jr.",
    "Colton Brewer": "Colten Brewer",
    "Dan Duffy": "Danny Duffy",
    "Daniel Winkler": "Dan Winkler",
    "Delino DeShields Jr": "Delino DeShields",
    "Enrique Kike Hernandez": "Kike Hernandez",
    "Felipe Rivero": "Felipe Vazquez",
    "Fernando Tatis Jr.": "Fernando Tatis",
    "Gregory Bird": "Greg Bird",
    "J.T. Chargois": "JT Chargois",
    "J.T. Riddle": "JT Riddle",
    "J.R. Murphy": "John Ryan Murphy",
    "Jake deGrom": "Jacob deGrom",
    "Jakob Junis": "Jake Junis",
    "Ji Man Choi": "Ji-Man Choi",
    "Jonathan Gray": "Jon Gray",
    "Jordan Adell": "Jo Adell",
    "Joshua Fields": "Josh Fields",
    "Kyle Barraclaugh": "Kyle Barraclough",
    "Leodys Taveras": "Leody Taveras",
    "Lourdes Jr Gurriel": "Lourdes Gurriel",
    "Marc Rzepcynski": "Marc Rzepczynski",
    "Mathew Skole": "Matt Skole",
    "Matt Bowman": "Matthew Bowman",
    "Michael Fiers": "Mike Fiers",
    "Mike Clevenger": "Michael Clevinger",
    "Mike Clevinger": "Michael Clevinger",
    "Mike Wacha": "Michael Wacha",
    "nAAAAthaniel Lowe": "Nathaniel Lowe",
    "Nate Eovaldi": "Nathan Eovaldi",
    "Nathan Orf": "Nate Orf",
    "Nick Castellanos": "Nicholas Castellanos",
    "Pat Corbin": "Patrick Corbin",
    "Pedro Avilan": "Luis Avilan",
    "Raul A. Mondesi": "Adalberto Mondesi",
    "Robert Refsnyder": "Rob Refsnyder",
    "Samuel Tuivailala": "Sam Tuivailala",
    "Seung Hwan Oh": "Seung-hwan Oh",
    "Steve Okert": "Steven Okert",
    "Triggs. Andrew": "Andrew Triggs",
    "Vincent Velasquez": "Vince Velasquez",
    "Williams Astudillo": "Willians Astudillo",
    "Yonothan Daza": "Yonathan Daza",
    "Yu-Cheng Chang": "Yu Chang",
    "Yulieski Gurriel": "Yuli Gurriel",
    "Zach Britton": "Zack Britton",
    "Zack Granite": "Zach Granite",
    "Rayne; Espinal": "Raynel Espinal",
    }

    player_name = ' '.join(reversed(reverse_name.split(', ')))
    if player_name in player_mapper:
        player_name = player_mapper.get(player_name)
    return player_name

if __name__ == "__main__":     
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2019)

    args = parser.parse_args()
    
    process(args.year)