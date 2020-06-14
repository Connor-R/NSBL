import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import logging

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

from py_db import db
import argparse
import NSBL_helpers as helper
import datetime

db = db('NSBL')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID of the roster spreadsheet
SAMPLE_SPREADSHEET_ID = '1Z9mjO4PLPs0WvAfWkcTTnoIqyI3vrRdATLJAvyCHiFk'

def process():

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    year = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='SUMMARY!A1').execute().get('values', [])[0][0]

    season_gp = db.query("SELECT gs FROM processed_league_averages_pitching WHERE year = %s" % (year))
    if season_gp == ():
        season_gp = 0
    else:
        season_gp = float(season_gp[0][0])/2

    date = datetime.datetime.now().date()

    teams = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='SUMMARY!C2:D31').execute().get('values', [])
    for tm in teams:
        team_name = tm[0]
        sheet_name = tm[1]

        print team_name
        team_abb = helper.get_team_abb(team_name)

        team_abb = tm[1]

        active_rng = sheet_name + '!A:H'
        active_players = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=active_rng).execute().get('values', [])

        process_players(active_players, year, season_gp, team_name, team_abb, date)

        reserve_rng = sheet_name + '!J:P'
        reserve_players = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=reserve_rng).execute().get('values', [])

        process_players(reserve_players, year, season_gp, team_name, team_abb, date)

    print '\nteam summary\n'
    summary = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='SUMMARY!A2:R31').execute().get('values', [])
    process_team_summary(summary, year, season_gp, date)


def process_team_summary(summary, year, season_gp, date):
    entries = []
    lg = ''
    div = ''
    for tm in summary:
        if tm[0].upper() == 'NATIONAL LEAGUE':
            lg = 'NL'
        elif tm[0].upper() == 'AMERICAN LEAGUE':
            lg = 'AL'

        if tm[1].upper() == 'EAST':
            div = 'East'
        elif tm[1].upper() == 'CENTRAL':
            div = 'Central'
        elif tm[1].upper() == 'WEST':
            div = 'West'

        entry = {'year': year, 'gp': season_gp, 'date': date, 'league': lg, 'division': div}

        cats = ['team_name', 'team_abb', 'base_cap', 'prev_reserves', 'buyout', 'traded_cash', 'total_cap', 'payroll', 'cap_room', 'debt_load', 'active_roster', 'reserve_roster', 'IL', 'Total']

        for i in range(0, 14):
            entry[cats[i]] = tm[i+2].replace('$','')

        if len(tm) < 17:
            GM = ''
        else:
            GM = tm[16]

        if len(tm) < 18:
            GM_email = ''
        else:
            GM_email = tm[17]

        entry['GM'] = GM
        entry['GM_email'] = GM_email

        entries.append(entry)

    if entries != []: 
        db.insertRowDict(entries, 'excel_team_summary', replace=True, insertMany=True, rid=0)
    db.conn.commit()


def process_players(player_list, year, season_gp, team_name, team_abb, date):
    entries = []
    pos = ''
    for plr in player_list:
        if plr[0] == 'Pitchers':
            pos = 'p'
        elif plr[0] == 'Catchers':
            pos = 'c'
        elif plr[0] == 'Infield':
            pos = 'if'
        elif plr[0] == 'Outfield':
            pos = 'of'

        try:
            if ((float(plr[2]) > 0 or plr[1] == 'MLI' or float(plr[3]) > 0) and plr[2] != ''):
                entry = {'year':year, 'gp':season_gp, 'position': pos, 'team_abb': team_abb, 'date': date}

                entered_name = plr[0]
                if pos == 'c' and entered_name == 'Smith, Will':
                    entered_name = 'D. Smith, Will'
                player_name, first_name, last_name = name_parser(entered_name)
                entry['player_name'] = player_name
                entry['fname'] = first_name
                entry['lname'] = last_name
                entry['entered_name'] = entered_name

                contract_year = plr[1]
                entry['contract_year'] = contract_year

                salary = plr[2]
                entry['salary'] = salary

                if len(plr) < 4:
                    expires = 0
                else:
                    expires = plr[3]

                if len(plr) < 5:
                    opt = ''
                else:
                    opt = plr[4]

                if len(plr) < 6:
                    ntc = None
                else:
                    ntc = plr[5]

                if len(plr) < 7:
                    salary_counted = 'N'
                else:
                    if plr[6] > 0 or (contract_year in ('V', 'CE', '4th', '5th', '6th') or contract_year[-1]=='G'):
                        salary_counted = 'Y'
                    else:
                        salary_counted = 'N'

                entry['expires'] = expires
                entry['opt'] = opt
                entry['ntc'] = ntc
                entry['salary_counted'] = salary_counted

                # for i,v in entry.items():
                #     print i, '\t', v

                entries.append(entry)

        except (IndexError, ValueError):
            continue

    if entries != []: 
        db.insertRowDict(entries, 'excel_rosters', replace=True, insertMany=True, rid=0)
    db.conn.commit()


def name_parser(reverse_name):
    player_mapper = {
    }

    first_name = reverse_name.split(', ')[1:]
    last_name = reverse_name.split(', ')[0]
    player_name = ' '.join(reversed(reverse_name.split(', ')))

    if player_name in player_mapper:
        first_name, last_name = player_mapper.get(player_name)
        player_name = first_name + ' ' + last_name
    return player_name, first_name, last_name

if __name__ == "__main__":     
    process()
