import xlrd
from py_db import db
import NSBL_helpers as helper

db = db('NSBL')

def process():
    rosters_link = '/Users/connordog/Dropbox/Desktop_Files/Baseball/Rosters.xls'

    curr_year = 2017

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
                option = team_sheet.cell(row, 5).value
                NTC = team_sheet.cell(row, 8).value
                salary_counted = team_sheet.cell(row, 9).value


                entry = {'player_name':player_name, "team_abb":primary_abb, "position":position, "salary":salary, "year":year, "expires":expires, "option":option, "NTC":NTC, "salary_counted":salary_counted}
                entries.append(entry)


        if entries != []: 
            db.insertRowDict(entries, 'current_rosters_excel', replace=True, insertMany=True, rid=0)
        db.conn.commit()


def name_parser(reverse_name):
    player_mapper = {
    "Michael Trout":"Mike Trout",
    "AJ Reed":"A.J. Reed",
    "Jackie Bradley Jr":"Jackie Bradley Jr.",
    "Matt Joyce":"Matthew Joyce",
    "Steven Souza Jr.":"Steven Souza",
    "Greg Bird":"Gregory Bird",
    "Jonathan Singleton":"Jon Singleton",
    "Steven Pearce":"Steve Pearce",
    "Jung-ho Kang":"Jung Ho Kang",
    "AJ Pollock":"A.J. Pollock",
    "Adam C. Eaton":"Adam Eaton",
    "Chris (86) Carter":"Chris Carter",
    "CJ Cron":"C.J. Cron",
    "Greg Polanco":"Gregory Polanco",
    "Steven Souza Jr":"Steven Souza",
    "Chris Young":"Chris B. Young",
    "Jonathon Schoop":"Jonathan Schoop",
    "Phillip Ervin":"Phil Ervin",
    "Matt M (91) Duffy":"Matt M. Duffy",
    "JJ Hardy":"J.J. Hardy",
    "Ozhaino Albies":"Ozzie Albies",
    }

    player_name = ' '.join(reversed(reverse_name.split(', ')))
    if player_name in player_mapper:
        player_name = player_mapper.get(player_name)
    return player_name

if __name__ == "__main__":     
    process()