from py_db import db
import argparse
from decimal import Decimal
import NSBL_helpers as helper
import itertools
from time import time


# script that determines the value for most reasonable lineups for all teams. 
# it uses some heuristics to limit the player list and then brute force finds the value of each lineup

db = db('NSBL')


def process():
    start_time = time()

    team_dict = {
        "2.75":('tam', 'tex'),
        "2.5":('pit', 'col', 'sea', 'mia', 'sd'),
        "2.0":('oak', 'nyn', 'cha', 'ari'),
        "1.8":('lan', 'lan'),
        "1.5":('bos', 'hou', 'was', 'chn', 'det', 'laa', 'mil', 'min', 'stl'),
        "1.0":('bal', 'kc', 'nya', 'cle', 'sf', 'tor'),
        "0.5":('atl', 'cin', 'phi')
        }

    i = 0 
    for min_war, team_tup in team_dict.items():
        min_war = float(min_war)

        team_q = """SELECT DISTINCT team_abb FROM teams 
        WHERE team_abb in %s
        AND year = 2017
        ORDER BY team_abb ASC
        """
        team_qry = team_q % (str(team_tup))
        # raw_input(team_qry)
        teams = db.query(team_qry)
        for team in teams:
            team_abb = team[0]

            temp_start = time()
            i += 1
            print i, team_abb

            process_lineups(team_abb, min_war)

            temp_end = time()
            temp_elapsed = float(temp_end - temp_start)
            print "\ttime elapsed (in seconds): " + str(temp_elapsed)
            print "\ttime elapsed (in minutes): " + str(temp_elapsed/60.0)

    end_time = time()

    elapsed_time = float(end_time - start_time)
    print "lineup_builder.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def process_lineups(team_abb, min_war):
    if team_abb == 'ChN':
        qry_add = "AND (t.team_abb = 'ChN' OR z.player_name = 'Jackie Bradley Jr.')"
    else:
        qry_add = "AND t.team_abb = '%s'" % team_abb
    q = """SELECT
    player_name, z.position, 
    WAR, vsL_WAR, vsR_WAR
    FROM zips_WAR_hitters z
    LEFT JOIN current_rosters USING (player_name, year)
    LEFT JOIN teams t USING (team_id, year)
    WHERE z.year = 2017
    %s
    AND (vsL_WAR > %s OR vsR_WAR > %s OR (z.position = '1b' AND WAR > 1.0) OR (z.position = 'c' AND WAR > 1.0) OR (z.position = 'dh' AND WAR > -0.5))
    ORDER BY position DESC, WAR DESC
    """

    qry = q % (qry_add, min_war, min_war)

    res = db.query(qry)

    _c, _1b, _2b, _3b, _ss, _rf, _cf, _lf, _dh = [], [], [], [], [], [], [], [], []
    _c2, _1b2, _2b2, _3b2, _ss2, _rf2, _cf2, _lf2, _dh2 = [], [], [], [], [], [], [], [], []
    for row in res:
        p = {}
        _name, _pos, _war, l_war, r_war = row
        key = _name + '_' + _pos
        p[_name]=[float(_war), float(l_war), float(r_war)]
        if _pos == 'c': _c.append(p), _c2.append(key)
        if _pos == '1b': _1b.append(p), _1b2.append(key)
        if _pos == '2b': _2b.append(p), _2b2.append(key)
        if _pos == '3b': _3b.append(p), _3b2.append(key)
        if _pos == 'ss': _ss.append(p), _ss2.append(key)
        if _pos == 'lf': _lf.append(p), _lf2.append(key)
        if _pos == 'cf': _cf.append(p), _cf2.append(key)
        if _pos == 'rf': _rf.append(p), _rf2.append(key)
        if _pos == 'dh': _dh.append(p), _dh2.append(key)

    _dh.append({"NONE":[0,0,0]})
    _dh2.append("NONE_dh")

    player_vals = [{'c':_c}, {'1b':_1b}, {'2b':_2b}, {'3b':_3b}, {'ss':_ss}, {'lf':_lf}, {'cf':_cf}, {'rf':_rf}, {'dh':_dh}]

    player_pos = [_c2, _1b2, _2b2, _3b2, _ss2, _lf2, _cf2, _rf2, _dh2]

    create_lu(team_abb, player_vals, player_pos)


def create_lu(team_abb, player_vals, player_pos):

    lineups = list(itertools.product(*player_pos))
    print '\t' + str(len(lineups)) + ' total lineups'

    entries = []
    i = 0
    for lu in lineups:
        i += 1
        if i % 1000000 == 1:
            if (i+1000000) > len(lineups):
                print '\t\tchecking lineups ' + str(i) + ' to ' + str(len(lineups))
            else:
                print '\t\tchecking lineups ' + str(i) + ' to ' + str(i+1000000-1)
        dupes = check_dupes(lu)
        if dupes is False:
            for vs_hand in ('l', 'r', 'all'):
                entry = enter_lineup(team_abb, vs_hand, lu, player_vals)
                entries.append(entry)

    print '\t' + str(len(entries)) + ' valid lineups'

    table = '__team_lineups'
    if entries != []:
        for i in range(0, len(entries), 2500):
            if (i+1) % 2500 == 1:
                if (i+1+2500) > len(entries):
                    print '\t\tentering lineups ' + str(i+1) + ' to ' + str(len(entries))
                else:
                    print '\t\tentering lineups ' + str(i+1) + ' to ' + str(i+2500)
            db.insertRowDict(entries[i: i + 2500], table, insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


def check_dupes(lu):
    players = []
    for p in lu:
        p_name = p.split('_')[0]
        players.append(p_name)

    if (len(players) == len(set(players)) and len(set(players)) == 9):
        return False
    else:
        return True


def enter_lineup(team_abb, vs_hand, lu, player_vals):
    entry = {}
    entry['team_abb'] = team_abb
    entry['vs_hand'] = vs_hand
    total_val = 0

    lineup = []
    lu_id = ''
    for p in lu:
        p_name, p_pos = p.split('_')
        for pos in player_vals:
            for keys, values in pos.items():
                if keys == p_pos:
                    for val in values:
                        for k, v in val.items():
                            if k == p_name:
                                if vs_hand == 'all':
                                    p_val = v[0]
                                elif vs_hand == 'l':
                                    p_val = v[1]
                                elif vs_hand == 'r':
                                    p_val = v[2]
                                total_val += p_val
                                lu_entry = {}
                                lu_entry[p_pos] = [p_name, p_val]
                                lu_id += p_name.replace(' ','')+'_'
                                lineup.append(lu_entry)


    lu_id = lu_id[0:-1]
    entry['lineup_val'] = total_val
    entry['c_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='c'][0]
    entry['c_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='c'][0]
    entry['1b_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='1b'][0]
    entry['1b_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='1b'][0]
    entry['2b_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='2b'][0]
    entry['2b_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='2b'][0]
    entry['3b_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='3b'][0]
    entry['3b_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='3b'][0]
    entry['ss_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='ss'][0]
    entry['ss_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='ss'][0]
    entry['lf_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='lf'][0]
    entry['lf_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='lf'][0]
    entry['cf_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='cf'][0]
    entry['cf_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='cf'][0]
    entry['rf_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='rf'][0]
    entry['rf_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='rf'][0]
    entry['dh_name'] = [l.values()[0][0] for l in lineup if l.keys()[0]=='dh'][0]
    entry['dh_WAR'] = [l.values()[0][1] for l in lineup if l.keys()[0]=='dh'][0]
    entry['lineup_id'] = lu_id

    return entry


if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    # parser.add_argument('--year',default=2017)
    args = parser.parse_args()
    
    process()
    