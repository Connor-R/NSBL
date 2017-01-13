from py_db import db
import pandas as pd
import argparse
import csv



db = db("NSBL")

def process():
    year = 2017
    for _type in ('offense','pitching','defense'):
        initiate(year, _type)
    
    # for year in range(2011,2017):
    #     for _type in ('offense','pitching','defense'):
    #         initiate(year, _type)


def initiate(year, _type):
    path = '/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/ad_hoc/historical_csv_files/'

    csv_file = path+'%s_zips_%s.csv'  % (year, _type)

    print year, _type

    entries = []
    with open(csv_file, 'rb') as f:
        mycsv = csv.reader(f)
        i = 0


        for row in mycsv:
            if i == 0:
                i += 1
                continue
            else:
                i += 1
                if _type == 'offense':
                    year, player_name, team_abb, g, ab, r, h, _2b, _3b, hr, rbi , bb, so , hbp, sb, cs, sh, sf, ibb, war = row 
                    entry = {"year":year, "player_name":player_name, "team_abb":team_abb, "g":g, "ab":ab, "r":r, "h":h, "2b":_2b, "3b":_3b, "hr":hr, "rbi":rbi, "bb":bb, "so":so, "hbp":hbp, "sb":sb, "cs":cs, "sh":sh, "sf":sf, "ibb":ibb, "zWAR":war}
                    entries.append(entry)

                elif _type == 'pitching':
                    year, player_name, team_abb, w, l, era, g, gs, ip, h, r, er, hr, bb, so, war = row 
                    entry = {"year":year, "player_name":player_name, "team_abb":team_abb, "w":w, "l":l, "era":era, "g":g, "gs":gs, "ip":ip, "h":h, "r":r, "er":er, "hr":hr, "bb":bb, "so":so, "zWAR":war}
                    entries.append(entry)

                elif _type == 'defense':
                    year, player_name, c_rn, c_er, _1b_rn, _1b_er, _2b_rn, _2b_er, _3b_er, _3b_rn, ss_rn, ss_er, lf_rn, lf_er, cf_rn, cf_er, rf_rn, rf_er, c_arm, of_arm, pb, FOO = row 
                    entry = {"year":year, "player_name":player_name, "c_range":c_rn, "c_error":c_er, "1b_range":_1b_rn, "1b_error":_1b_er, "2b_range":_2b_rn, "2b_error":_2b_er, "3b_range":_3b_rn, "3b_error":_3b_er, "ss_range":ss_rn, "ss_error":ss_er, "lf_range":lf_rn, "lf_error":lf_er, "cf_range":cf_rn, "cf_error":cf_er, "rf_range":rf_rn, "rf_error":rf_er, "c_arm":c_arm, "of_arm":of_arm, "c_pb":pb}
                    entries.append(entry)
                # print i, _type, player_name

    table = 'zips_%s_%s' % (_type, year)
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()


if __name__ == "__main__":        

    process()