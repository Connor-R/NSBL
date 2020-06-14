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
            player_name, first_name, last_name = name_parser(entered_name, primary_abb)

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


def name_parser(reverse_name, primary_abb):
    player_map = {
    }


    first_name = reverse_name.split(', ')[1:]
    last_name = reverse_name.split(', ')[0]
    player_name = ' '.join(reversed(reverse_name.split(', ')))

    if player_name in player_map:
        first_name, last_name = player_map.get(player_name)
        player_name = first_name + ' ' + last_name
    return player_name, first_name, last_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year',type=int,default=2020)

    args = parser.parse_args()
    
    process(args.year)