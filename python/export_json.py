#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import psycopg2
import datetime
import collections
from os.path import join
from json import dumps

DBHOST = "localhost"
DBPORT = "5432"
DBNAME = "rosebud2"
DBUSER = "stefan"
DBPWD = "ziegler12"

OUT_DIR = '/home/stefan/Projekte/qgis_server_statistics/html/'

sql_daily = """SELECT EXTRACT(EPOCH FROM t1.cumulative_datetime) * 1000::integer as cumulative_datetime, coalesce(t2.count, 0) as count
--FROM generate_series(NOW() - '1 day'::INTERVAL, NOW(), '15min') AS t1(cumulative_datetime)
FROM generate_series('2014-07-15 14:00:00'::timestamp,'2014-07-16 14:00:00'::timestamp, '15min') AS t1(cumulative_datetime)
LEFT OUTER JOIN 
(
 SELECT count(*), round(extract('epoch' from request_date) / 900),  timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 900) * 900 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
-- Das geht wirklich nur mit NOW().
--WHERE request_date >= NOW() - '1 day'::INTERVAL
-- Zum testen:
 WHERE request_date >= '2014-07-15 14:00:00'::timestamp 
 AND request_date <= '2014-07-16 14:00:00'::timestamp 
 GROUP BY round(extract('epoch' from request_date) / 900)
 ORDER BY round(extract('epoch' from request_date) / 900)
) AS t2
ON  t1.cumulative_datetime =  t2.cumulative_datetime
ORDER BY t1.cumulative_datetime;
"""

try:
    
    con_string = "host='" + DBHOST + "' dbname='" + DBNAME + "' user='" + DBUSER + "' password='" + DBPWD + "'"
    con = psycopg2.connect( con_string )
    
    cur = con.cursor()
    cur.execute(sql_daily)
    rows = cur.fetchall()

    rowarray_list = []
    for row in rows:
        t = (row[0],  row[1])
#        t = (row.ID, row.FirstName, row.LastName, row.Street, 
#             row.City, row.ST, row.Zip)
        rowarray_list.append(t)



    chart_list = []
    
    d = collections.OrderedDict()
    d['key'] =  "Total / 15min"
    d['color'] = "#3182bd"
    d['area'] = True
    d['values'] = rowarray_list
        
    chart_list.append(d)
    
    with open(join(OUT_DIR,  "daily.json" ), "w") as file:
        file.write(dumps(chart_list, file, indent=4))


except psycopg2.DatabaseError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value

except IOError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value
    
finally:
    if con:
        con.close()
