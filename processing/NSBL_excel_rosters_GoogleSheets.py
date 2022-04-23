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
SAMPLE_SPREADSHEET_ID = '1yCxpH7Z11npATz_rYJZiGlq64LtoT8nQNvGAyZkqTv4'

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
        if plr == []:
            continue
        if plr[0] == 'Pitchers':
            pos = 'p'
        elif plr[0] == 'Catchers':
            pos = 'c'
        elif plr[0] == 'Infield':
            pos = 'if'
        elif plr[0] == 'Outfield':
            pos = 'of'


        try:
            if (plr[1] == 'MLI') or ((float(plr[2]) > 0 or float(plr[3]) > 0) and plr[2] != ''):
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
                if player_name == 'Max Stassi':
                    contract_year = 'V'
                entry['contract_year'] = contract_year

                if plr[1] == 'MLI':
                    salary = 1.1
                else:
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


                # if len(plr) < 7:
                    # salary_counted = 'N'
                # else:
                salary_counted = 'N'
                if (contract_year.lower() in ('v', 'ce', '4th', '5th', '6th') or contract_year[-1]=='G'):
                    salary_counted = 'Y'


                entry['expires'] = expires
                entry['opt'] = opt
                entry['ntc'] = ntc
                entry['salary_counted'] = salary_counted

                # for i,v in entry.items():
                #     print i, '\t', v

                helper.input_name(entry.get('player_name'))
                entries.append(entry)

        except (IndexError, ValueError):
            continue

    if entries != []: 
        db.insertRowDict(entries, 'excel_rosters', replace=True, insertMany=True, rid=0)
    db.conn.commit()


def update_names():
    queries = """update excel_rosters er
        join name_mapper nm on (1
            and if(entered_name like "%,%"
            , concat(trim(substring(entered_name from instr(entered_name, ',') + 1)), ' ', trim(substring_index(entered_name, ',', 1))) # search name
            , entered_name
            ) = nm.wrong_name
        )
        set player_name = concat(nm.right_fname, ' ', nm.right_lname)
        , fname = nm.right_fname
        , lname = nm.right_lname
        ;
    """

    print '\n\tupdating excel roster names'
    for q in queries.split(";"):
        if q.strip() != "":
            # print(q)
            db.query(q)
            db.conn.commit()


def yearly_contracts():
    queries = """drop table if exists yearly_contracts;
        create table yearly_contracts (index idx(player_name, year)) as
        select year
        , player_name
        , pos2
        , salary
        , replace(contract_year, '-g', '') as contract_year
        , expires
        , opt
        , ntc
        from(   
            select b.*
            , if(@pos = pos2 and @yr = year and @plr = player_name, @cnt := @cnt+1, @cnt := 1) as cnt
            , @pos := pos2 as pos_set
            , @yr := year as yr_set
            , @plr := player_name as plr_set
            from(
                select distinct a.*
                , case
                    when overlap = 'yes' then 0
                    when contract_year = 'ce' then 1
                    when ntc is not null then 2
                    when replace(contract_year, '-g', '') = 'v' and (expires > year or expires = year and opt not in ('no', '')) then 3
                    when expires = 0 and contract_year != 'MLI' then 4
                    when replace(contract_year, '-g', '') = 'v' and expires = year then 5
                else 6
                end as ordering
                , @pos := '' as pos_init
                , @yr := 0 as yr_init
                , @plr := '' as plr_init
                , @cnt := 0 as cnt_init
                from(
                    select *
                    , null as overlap
                    , if(position = 'p', 'p', 'h') as pos2
                    from excel_rosters
                    union all
                    select year-1 as `year`
                    , gp
                    , concat(year-1, '-12-31') as `date`
                    , player_name
                    , fname
                    , lname
                    , team_abb
                    , position
                    , salary
                    , contract_year
                    , expires
                    , opt
                    , ntc
                    , salary_counted
                    , entered_name
                    , 'yes' as overlap
                    , if(position = 'p', 'p', 'h') as pos2
                    from excel_rosters
                    where 1
                        and gp = 0
                        and contract_year in ('ce', 'v')
                        and month(date) = 1
                        and day(date) = 1
                    group by year, player_name
                    order by player_name, year
                ) a
                where 1
                order by year, player_name, ordering asc
            ) b
        ) c
        where 1
            and cnt = 1
        ;
    """

    print '\n\tadding yearly_contracts table'
    for q in queries.split(";"):
        if q.strip() != "":
            # print(q)
            db.query(q)
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

    update_names()

    yearly_contracts()
