import sys
import argparse
from decimal import Decimal
from time import time

sys.path.append('/Users/connordog/Dropbox/Desktop_Files/Work_Things/CodeBase/Python_Scripts/Python_Projects/packages')

from py_db import db
db = db('NSBL')

def initiate():
    start_time = time()

    process_hitters()
    process_pitchers()

    end_time = time()
    elapsed_time = float(end_time - start_time)
    print "time elapsed (in seconds): " + str(elapsed_time)
    print "time elapsed (in minutes): " + str(elapsed_time/60.0)


def process_pitchers():
    entries = []
    query = """SELECT year, player_id, blurb 
    FROM(
        SELECT * FROM _professional_prospects
        UNION ALL SELECT * FROM _draft_prospects
        UNION ALL SELECT * FROM _international_prospects
    ) prospects
    WHERE LEFT(position,3) IN ('RHP','LHP')
    """
    res = db.query(query)    

    for row in res:
        entry = {}
        year, player_id, blurb = row

        print player_id, year

        entry["year"] = year
        entry["player_id"] = player_id

        if player_id in (None, 0):
            continue

        if blurb[:4] == '\nPDP':
            continue

        try:
            overall_text = blurb.split("Overall")[1].split('\n')[0].replace(':','').replace(' ','')[:8]
            if overall_text[0] not in (' ',':','0','1','2','3','4','5','6','7','8','9'):
                raise IndexError

            try:
                text2 = overall_text.split('/')[1]
            except IndexError:
                text2 = overall_text.split('/')[-1]

            overall = int(filter(str.isdigit, text2[:2]))
        except IndexError:
            overall = 0

        if overall < 20 and overall is not None:
            overall = overall*10
        entry["overall"] = overall


        try:
            try:
                control = int(blurb.split("Control")[1].split("|")[0].split('/')[-1].replace(':','').replace(' ','')[:8])
            except IndexError:
                control = int(blurb.split("Cont.")[1].split("|")[0].split('/')[-1].replace(':','').replace(' ','')[:8])
            except ValueError:
                control = int(blurb.split("Control")[1].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:2])
        except IndexError:
            control = 0
        if control < 20 and control is not None:
            control = control*10
        entry["control"] = control


        try:
            fastball = int(blurb.split("Fastball")[1].split("|")[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            try:
                fastball = int(blurb.split("FB")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
            except IndexError:
                fastball = None
        if fastball < 20 and fastball is not None:
            fastball = fastball*10
        entry["fastball"] = fastball


        try:
            change = int(blurb.split("Changeup")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            try:
                change = int(blurb.split("Change")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
            except IndexError:
                change = None
        if change < 20 and change is not None:
            change = change*10
        entry["change"] = change


        try:
            curve = int(blurb.split("Curveball")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            try:
                curve = int(blurb.split("Curve")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
            except IndexError:
                curve = None
        if curve < 20 and curve is not None:
            curve = curve*10
        entry["curve"] = curve


        try:
            slider = int(blurb.split("Slider")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            slider = None
        if slider < 20 and slider is not None:
            slider = slider*10
        entry["slider"] = slider


        try:
            cutter = int(blurb.split("Cutter")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            cutter = None
        if cutter < 20 and cutter is not None:
            cutter = cutter*10
        entry["cutter"] = cutter


        try:
            splitter = int(blurb.split("Splitter")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            splitter = None
        if splitter < 20 and splitter is not None:
            splitter = splitter*10
        entry["splitter"] = splitter


        try:
            other = int(blurb.split("Screwball")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            try:
                other = int(blurb.split("Knuckle")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
            except IndexError:
                try:
                    other = int(blurb.split("Palmball")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
                except IndexError:
                    other = None
        if other < 20 and other is not None:
            other = other*10
        entry["other"] = other

        entries.append(entry)

    if entries != []:
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i: i + 1000], '_prospect_pitcher_grades', insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


def process_hitters():
    entries = []
    query = """SELECT year, player_id, blurb 
    FROM(
        SELECT * FROM _professional_prospects
        UNION ALL SELECT * FROM _draft_prospects
        UNION ALL SELECT * FROM _international_prospects
    ) prospects
    WHERE LEFT(position,3) NOT IN ('RHP','LHP')
    """
    res = db.query(query)

    for row in res:
        entry = {}
        year, player_id, blurb = row

        entry["year"] = year
        entry["player_id"] = player_id

        if player_id in (None, 0):
            continue

        if blurb[:4] == '\nPDP':
            continue

        hit = int(blurb.split("Hit")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        if hit < 20:
            hit = hit*10
        power = int(blurb.split("Power")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        if power < 20:
            power = power*10
        try:
            run = int(blurb.split("Run")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            run = int(blurb.split("Speed")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        if run < 20:
            run = run*10
        arm = int(blurb.split("Arm")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        if arm < 20:
            arm = arm*10
        try:
            field = int(blurb.split("Field")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except IndexError:
            field = int(blurb.split("Defense")[1].split("|")[0].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:8])
        except ValueError:
            field = int(blurb.split("Field")[1].split('\n')[0].split('/')[-1].replace(':','').replace(' ','')[:2])
        if field < 20:
            field = field*10

        entry["hit"] = hit
        entry["power"] = power
        entry["run"] = run
        entry["arm"] = arm
        entry["field"] = field

        try:
            overall_text = blurb.split("Overall")[1].split('\n')[0].replace(':','').replace(' ','')[:8]
            if overall_text[0] not in (' ',':','0','1','2','3','4','5','6','7','8','9'):
                raise IndexError

            try:
                text2 = overall_text.split('/')[1]
            except IndexError:
                text2 = overall_text.split('/')[-1]

            overall = int(filter(str.isdigit, text2[:2]))
        except IndexError:
            overall = 0

        if overall < 20:
            overall = overall*10

        entry["overall"] = overall

        entries.append(entry)

    if entries != []:
        for i in range(0, len(entries), 1000):
            db.insertRowDict(entries[i: i + 1000], '_prospect_hitter_grades', insertMany=True, replace=True, rid=0,debug=1)
            db.conn.commit()


if __name__ == "__main__":        
   
    initiate()
    