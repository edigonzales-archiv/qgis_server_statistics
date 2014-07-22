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

sql_day = """
SELECT t1.my_datetime * 60 * 1000, coalesce(t2.count, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 60) as my_datetime
 FROM generate_series(NOW() - '1 day'::INTERVAL, NOW(), '60sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 60) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 60) * 60 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 day'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 60)
 ORDER BY round(extract('epoch' from request_date) / 60)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;
"""

sql_week = """
SELECT t1.my_datetime * 60 * 1000, coalesce(t2.count, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 60) as my_datetime
 FROM generate_series(NOW() - '1 week'::INTERVAL, NOW(), '60sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 60) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 60) * 60 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 week'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 60)
 ORDER BY round(extract('epoch' from request_date) / 60)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;
"""

# 1800 sek / 30 = 60 sek. 
# Weniger Punkte aber trotzdem 'pro Minute' (entspricht dann halt dem Durchschnitt in diesen 1800 sekunden)
sql_month = """
SELECT t1.my_datetime * 1800 * 1000, coalesce(t2.count / 30, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 1800) as my_datetime
 FROM generate_series(NOW() - '1 month'::INTERVAL, NOW(), '1800sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 1800) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 1800) * 1800 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 month'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 1800)
 ORDER BY round(extract('epoch' from request_date) / 1800)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;
"""

# count / 120 -> dann erhält man den Durchnitt in den zwei Stunden?????
sql_year = """
SELECT t1.my_datetime * 7200 * 1000, coalesce(t2.count / 120, 0) as count 
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 7200) as my_datetime
 FROM generate_series(NOW() - '1 year'::INTERVAL, NOW(), '7200sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 7200) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 7200) * 7200 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 year'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 7200)
 ORDER BY round(extract('epoch' from request_date) / 7200)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;
"""

try:
    
    con_string = "host='" + DBHOST + "' dbname='" + DBNAME + "' user='" + DBUSER + "' password='" + DBPWD + "'"
    con = psycopg2.connect( con_string )
    
    cur = con.cursor()
    cur.execute(sql_year)
    rows = cur.fetchall()

    rowarray_list = []
    for row in rows:
        t = (row[0],  row[1])
#        t = (row.ID, row.FirstName, row.LastName, row.Street, 
#             row.City, row.ST, row.Zip)
        rowarray_list.append(t)



    chart_list = []
    
    d = collections.OrderedDict()
    d['key'] =  "Total / min"
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
