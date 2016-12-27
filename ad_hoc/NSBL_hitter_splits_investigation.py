from py_db import db
import pandas as pd
import argparse


# Investigating the nature of splits in the NSBL

db = db('NSBL')

def process(start_year, end_year, path):

    q = """ SELECT 
SUM(ab) AS ab,
SUM(h) AS h,
SUM(2b) AS 2b,
SUM(3b) AS 3b, 
SUM(hr) AS hr,
SUM(bb) AS bb,
SUM(k) AS k,
CASE 
    WHEN RIGHT(player_name, 1) = '*' THEN 'L' 
    WHEN RIGHT(player_name, 1) = '#' THEN 'S'
    ELSE 'R'
    END AS bats,
vs_hand
FROM register_batting_splits
WHERE year >= %s
AND year <= %s
GROUP BY bats, vs_hand;
"""

    qry = q % (start_year, end_year)

    query = db.query(qry)


    cols = ['bats','vs_hand','pa','avg','obp','slg','k_perc','bb_perc','hr_perc','woba']
    data = {'bats': [],
            'vs_hand': [],
            'pa': [],
            'avg': [],
            'obp': [],
            'slg': [],
            'k_perc': [],
            'bb_perc': [],
            'hr_perc': [],
            'woba': []
            }


    for row in query:
        row_data = []
        ab, h, _2b, _3b, hr, bb, k, bats, vs_hand = row


        
        _1b = h - _2b - _3b - hr

        pa = ab + bb

        avg = float(h)/float(ab)
        obp = (float(h)+float(bb))/float(pa)
        slg = (float(_1b)+2*float(_2b)+3*float(_3b)+4*float(hr))/float(pa)

        hr_perc = float(hr)/float(ab)
        bb_perc = float(bb)/float(pa)
        k_perc = float(k)/float(ab)

        woba = ((0.691*float(bb) + 0.884*float(_1b) + 1.257*float(_2b) + 1.593*float(_3b) + 2.058*float(hr))/float(pa))

        row_data.append(bats)
        row_data.append(vs_hand)
        row_data.append(pa)
        row_data.append(avg)
        row_data.append(obp)
        row_data.append(slg)
        row_data.append(k_perc)
        row_data.append(bb_perc)
        row_data.append(hr_perc)
        row_data.append(woba)


        for att, i in zip(cols, range(0,10)):
            data[att].append(row_data[i])


    splits = pd.DataFrame(data, columns = cols)

    print '\n\n\n' + 'FROM ' + str(start_year) + ' TO ' + str(end_year)

    pd.set_option('display.width', 1000)
    print splits
    print '\n\n'


if __name__ == "__main__":        



    parser = argparse.ArgumentParser()
    parser.add_argument('--start_year',default=2014 )
    parser.add_argument('--end_year',default=2016 )
    parser.add_argument('--path',default='/Users/connordog/Desktop/')    
    args = parser.parse_args()
    
    process(args.start_year, args.end_year, args.path)