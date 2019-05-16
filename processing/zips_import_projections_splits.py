from py_db import db
import pandas as pd
import argparse
import csv
from time import time

# loading script for importing zips pitching/hitting splits from csv files


db = db("NSBL")


def process(player_mapper):
    start_time = time()

    year = 2019
    for _type in ('offense','pitching'):
        initiate(year, _type, player_mapper)
    
    # for year in range(2014,2018):
    #     for _type in ('offense','pitching'):
    #         initiate(year, _type, player_mapper)

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "zips_import_projections_splits.py"
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def initiate(yr, _type, player_mapper):
    path = '/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/NSBL/ad_hoc/historical_csv_files/'

    csv_file = path+'%s_zips_%s_splits.csv'  % (yr, _type)

    print yr, _type

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
                year, player_name, vs_hand, ab, h, _2b, _3b, hr, rbi , bb, so , hbp, ibb, sh, sf = row
                if player_name in player_mapper:
                    player_name = player_mapper.get(player_name) 
                entry = {"year":yr, "player_name":player_name, "vs_hand":vs_hand, "ab":ab, "h":h, "2b":_2b, "3b":_3b, "hr":hr, "rbi":rbi, "bb":bb, "so":so, "hbp":hbp, "ibb":ibb, "sh":sh, "sf":sf}
                entries.append(entry)


    table = 'zips_%s_splits' % (_type)
    if entries != []: 
        db.insertRowDict(entries, table, replace=True, insertMany=True, rid=0)
    db.conn.commit()


if __name__ == "__main__":        
    player_mapper = {
    "Brock Holt!":"Brock Holt",
    "Tyler Holt ?!?":"Tyler Holt"
    }      

    process(player_mapper)