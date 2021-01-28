from py_db import db
from fuzzywuzzy import fuzz
import csv
from time import time

db = db("NSBL")

start_time = time()

with open('names.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile)
    filewriter.writerow(['SimScore', 'ID1', 'Inp1', 'F1', 'L1', 'ID2', 'Inp2', 'F2', 'L2', 'F_score', 'L_score'])

    query = """SELECT n.name_mapper_id AS id1
        , n.wrong_name as inp1
        , n.right_fname as f1
        , n.right_lname as l1
        , n2.name_mapper_id AS id2
        , n2.wrong_name as inp2
        , n2.right_fname as f2
        , n2.right_lname as l2
        FROM name_mapper n
        JOIN name_mapper n2 
        WHERE 1
            AND n.name_mapper_id < n2.name_mapper_id
            AND CONCAT(n.right_fname, ' ', n.right_lname) != CONCAT(n2.right_fname, ' ', n2.right_lname)
            AND (LEFT(n.right_fname,2) = LEFT(n2.right_fname,2) OR LEFT(n.right_lname,2) = LEFT(n2.right_lname,2))
        ;"""

    res = db.query(query)

    for i, row in enumerate(res):
        if i % 5000 == 0:
            print i, 'of', len(res)
        p1 = row[2] + ' ' + row[3]
        p2 = row[6] + ' ' + row[7]
        sim_score = fuzz.ratio(p1, p2)
        fname_score = fuzz.ratio(row[2], row[6])
        lname_score = fuzz.ratio(row[3], row[7])
        if sim_score > 95 or (fname_score > 60 and lname_score > 95):
            print '\t', sim_score
            print '\t\t id1:', row[0], '\tinp1:', row[1], '\tp1:', p1
            print '\t\t id2:', row[4], '\tinp2:', row[5], '\tp2:', p2
            csvrow = list(row)
            csvrow = [sim_score] + csvrow + [fname_score] + [lname_score]
            filewriter.writerow(csvrow)


end_time = time()
elapsed_time = float(end_time - start_time)
print "time elapsed (in seconds): " + str(elapsed_time)
print "time elapsed (in minutes): " + str(elapsed_time/60.0)