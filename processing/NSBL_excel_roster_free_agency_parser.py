import xlrd
from py_db import db
import NSBL_helpers as helper

db = db('NSBL')

def process():
    rosters_link = '/Users/connordog/Dropbox/Desktop_Files/Baseball/Rosters.xls'

    curr_year = 2017

    #Each time we run this, we clear the free agency tables
    db.query("TRUNCATE TABLE `free_agency_curr`")
    db.query("TRUNCATE TABLE `free_agency_plus1`")
    db.query("TRUNCATE TABLE `free_agency_plus2`")

    workbook = xlrd.open_workbook(rosters_link)

    # iterate through all team sheets
    for index in range(4, 34):
        team_name = workbook.sheet_names()[index]

        print team_name

        team_abbs, primary_abb = helper.get_team_abbs(team_name.upper())

        entries_curr = []
        entries_plus1 = []
        entries_plus2 = []

        team_sheet = workbook.sheet_by_index(index)

        # get a maximum row for each sheet
        for row in range(1,100):
            if team_sheet.cell(row,1).value == 'Free Agents':
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

            salary = team_sheet.cell(row, 3).value

            reverse_name = team_sheet.cell(row, 1).value
            player_name = name_parser(reverse_name)

            if team_sheet.cell(row, 2).value == '6th':
                entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":"6th", "position":position, "salary":salary}
                entries_curr.append(entry)

            if team_sheet.cell(row, 2).value == '5th':
                entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":"5th", "position":position, "salary":salary}
                entries_plus1.append(entry)

            if team_sheet.cell(row, 2).value == '4th':
                entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":"4th", "position":position, "salary":salary}
                entries_plus2.append(entry)

            if team_sheet.cell(row, 4).value == curr_year:
                if team_sheet.cell(row, 5).value == '':
                    entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":str(curr_year), "position":position, "salary":salary}
                else:
                    entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":str(curr_year)+"-opt", "position":position, "salary":salary}
                entries_curr.append(entry)

            if team_sheet.cell(row, 4).value == curr_year+1:
                if team_sheet.cell(row, 5).value == '':
                    entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":str(curr_year+1), "position":position, "salary":salary}
                else:
                    entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":str(curr_year+1)+"-opt", "position":position, "salary":salary}
                entries_plus1.append(entry)

            if team_sheet.cell(row, 4).value == curr_year+2:
                if team_sheet.cell(row, 5).value == '':
                    entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":str(curr_year+2), "position":position, "salary":salary}
                else:
                    entry = {'player_name':player_name, "team_abb":primary_abb, "fa_type":str(curr_year+2)+"-opt", "position":position, "salary":salary}
                entries_plus2.append(entry)

        if entries_curr != []: 
            db.insertRowDict(entries_curr, 'free_agency_curr', replace=True, insertMany=True, rid=0)
        db.conn.commit()

        if entries_plus1 != []: 
            db.insertRowDict(entries_plus1, 'free_agency_plus1', replace=True, insertMany=True, rid=0)
        db.conn.commit()

        if entries_plus2 != []: 
            db.insertRowDict(entries_plus2, 'free_agency_plus2', replace=True, insertMany=True, rid=0)
        db.conn.commit()


def name_parser(reverse_name):
    player_name = ' '.join(reversed(reverse_name.split(', ')))
    return player_name

if __name__ == "__main__":     
    process()