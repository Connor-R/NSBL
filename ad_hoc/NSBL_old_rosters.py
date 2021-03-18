import xlrd
from py_db import db
import argparse
import NSBL_helpers as helper
import datetime

db = db('NSBL')


def process():

    for szn, deets in {2008: [5, 'xls', 0, 1]
        , 2009: [5, 'xls', 0, 1]
        , 2010: [4, 'xls', 0, 1]
        , 2011: [4, 'xls', 0, 1]
        , 2012: [4, 'xls', 0, 1]
        , 2013: [3, 'xls', 0, 1]
        , 2014: [3, 'xls', 0, 1]
        , 2015: [4, 'xls', 1, 8]
        , 2016: [4, 'xls', 1, 8]
        , 2017: [4, 'xlsx', 1, 8]
        , 2018: [4, 'xls', 1, 8]
        , 2019: [4, 'xlsx', 1, 8]
    }.items():

        print '\n'
        print(szn)
        print '\n'

        start_sheet, ext, first_col, first_row = deets

        rosters_link = '/Users/connordog/Dropbox/Desktop_Files/Baseball/Old_Rosters/%s%s-Offseason.%s' % (szn, szn+1, ext)

        season_gp = 0

        date = datetime.datetime(szn, 12, 1)

        workbook = xlrd.open_workbook(rosters_link)

        # iterate through all team sheets
        for i, index in enumerate(range(start_sheet, start_sheet+30)):

            mascot_name = workbook.sheet_names()[index]

            if mascot_name == 'BlueJays':
                mascot_name = 'Blue Jays'
            elif mascot_name == 'WhiteSox':
                mascot_name = 'White Sox'
            elif mascot_name == 'RedSox':
                mascot_name = 'Red Sox'

            print '\t', i+1, mascot_name
            # raw_input('')

            team_name = helper.get_team(mascot_name, szn)

            team_abb = helper.get_team_abb(team_name, szn)

            entries = []

            team_sheet = workbook.sheet_by_index(index)

            # get a maximum row for each sheet
            for row in range(1,100):
                if team_sheet.cell(row, first_col).value in ('Waived Players', 'Free Agents'):
                    max_row = row
                    break

            position = ''
            for row in range(first_row, max_row):
                if team_sheet.cell(row, first_col).value == 'Pitchers':
                    position = 'p'
                if team_sheet.cell(row, first_col).value == 'Catchers':
                    position = 'c'
                if team_sheet.cell(row, first_col).value == 'Infielders':
                    position = 'if'
                if team_sheet.cell(row, first_col).value == 'Outfielders':
                    position = 'of'




                if team_sheet.cell(row, first_col+1).value not in ('Year','') and team_sheet.cell(row, first_col+2).value not in ('Salary', ''):

                    year = team_sheet.cell(row, first_col+1).value

                    if year == '3rdd':
                        year = '3rd'

                    if year.lower().strip() not in ('v', 'ce', '6th', '5th', '4th', '3rd', '2nd', '1st', 'xxx'):
                        if year.lower() not in ('salary', 'salary cap', 'cap room', 'debt load', 'payroll'):
                            print '\n\t\t\t\t\t\t', year, '\n'
                            raw_input('')
                        continue

                    entered_name = team_sheet.cell(row, first_col).value.replace('  ', ' ')
                    if position == 'c' and entered_name == 'Smith, Will':
                        entered_name = 'D. Smith, Will'

                    # print '\t', entered_name
                    player_name, first_name, last_name = name_parser(entered_name)

                    salary = team_sheet.cell(row, first_col+2).value
                    expires = team_sheet.cell(row, first_col+3).value
                    opt = team_sheet.cell(row, first_col+4).value
                    NTC = team_sheet.cell(row, first_col+7).value
                    salary_counted = team_sheet.cell(row, first_col+8).value




                    entry = {'year':szn, 'gp':season_gp, 'player_name':player_name, "fname":first_name, "lname":last_name, "team_abb":team_abb,  "position":position, "salary":salary, "contract_year":year, "expires":expires, "opt":opt, "NTC":NTC, "salary_counted":salary_counted, "entered_name":entered_name, "date":date}

                    helper.input_name(entry.get('player_name'))

                    entries.append(entry)


            # raw_input(entries)
            if entries != []: 
                db.insertRowDict(entries, 'excel_rosters', replace=True, insertMany=True, rid=0)
            db.conn.commit()

        process_team_summary(workbook.sheet_by_index(0), szn, 0, date)



def process_team_summary(summary, year, season_gp, date):
    entries = []
    lg = ''
    div = ''

    cat_dict = {2008:[3, 0, ['team_name', 'cap_room', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM']]
        , 2009: [3, 0, ['team_name', 'cap_room', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM']]
        , 2010: [3, 0, ['team_name', 'cap_room', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM']]
        , 2011: [3, 0, ['team_name', 'cap_room', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM', 'GM_email']]
        , 2012: [3, 0, ['team_name', 'cap_room', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM', 'GM_email']]
        , 2013: [3, 0, ['team_name', 'cap_room', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM', 'GM_email']]
        , 2014: [3, 0, ['team_name', 'cap_room', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM', 'GM_email']]
        , 2015: [3, 0, ['team_name', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'cap_room', 'active_roster', 'reserve_roster', 'IL', 'foo', 'GM', 'GM_email']]
        , 2016: [3, 0, ['team_name', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'cap_room', 'active_roster', 'reserve_roster', 'IL', 'Total', 'foo', 'GM', 'GM_email']]
        , 2017: [3, 0, ['team_name', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'cap_room', 'active_roster', 'reserve_roster', 'IL', 'Total', 'foo', 'GM', 'GM_email']]
        , 2018: [3, 0, ['team_name', 'base_cap', 'prev_reserves', 'traded_cash', 'total_cap', 'payroll', 'cap_room', 'active_roster', 'reserve_roster', 'IL', 'Total', 'foo', 'GM', 'GM_email']]
        , 2019: [3, 0, ['team_name', 'base_cap', 'prev_reserves', 'buyout', 'traded_cash', 'total_cap', 'payroll', 'cap_room', 'active_roster', 'reserve_roster', 'IL', 'Total', 'foo', 'GM', 'GM_email']]
    }

    summary_row, summary_column, cats = cat_dict.get(year)

    for row in range(summary_row,summary_row+30):

        if summary.cell(row, 0).value.upper() in ('NATIONAL LEAGUE', 'NL'):
            lg = 'NL'
        elif summary.cell(row, 0).value.upper() in ('AMERICAN LEAGUE', 'AL'):
            lg = 'AL'

        if summary.cell(row, 1).value.upper() in ('EAST', 'E'):
            div = 'East'
        elif summary.cell(row, 1).value.upper() in ('CENTRAL', 'C'):
            div = 'Central'
        elif summary.cell(row, 1).value.upper() in ('WEST', 'W'):
            div = 'West'

        entry = {'year': year, 'gp': season_gp, 'date': date, 'league': lg, 'division': div}

        for i in range(0, len(cats)):
            if cats[i] == 'foo':
                continue

            val = summary.cell(row, summary_column+2+i).value
            if type(val) == 'str':
                val = val.replace(' players', '').replace(' on DL', '').replace('$', '')
            entry[cats[i]] = val

        team_abb = helper.get_team_abb(entry['team_name'], year)
        entry['team_abb'] = team_abb

        entries.append(entry)

    if entries != []: 
        db.insertRowDict(entries, 'excel_team_summary', replace=True, insertMany=True, rid=0)
    db.conn.commit()



def name_parser(reverse_name):
    player_mapper = {
    }

    qry = """SELECT wrong_name
    , right_fname
    , right_lname
    FROM name_mapper nm
    ;"""

    res = db.query(qry)
    for row in res:
        wrong, right_fname, right_lname = row
        player_mapper[wrong] = [right_fname, right_lname]

    
    first_name = reverse_name.split(', ')[1:]
    last_name = reverse_name.split(', ')[0]
    player_name = ' '.join(reversed(reverse_name.split(', ')))

    if player_name in player_mapper:
        first_name, last_name = player_mapper.get(player_name)
        player_name = first_name + ' ' + last_name
    return player_name, first_name, last_name


if __name__ == "__main__":     
    process()
