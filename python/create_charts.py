#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import psycopg2
import datetime
import csv
from os.path import join

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DBHOST = "localhost"
DBPORT = "5432"
DBNAME = "rosebud2"
DBUSER = "stefan"
DBPWD = "ziegler12"

TMPPATH = '/home/stefan/tmp/'

sql_day_all = """SELECT s.hour::int, coalesce(t.value, 0)
FROM generate_series(0,23) AS s(hour) 
LEFT OUTER JOIN 
(
  SELECT COUNT(ogc_fid) AS value, EXTRACT(hour FROM request_date) AS hour 
  FROM qgis_server_statistics.wms_stats WHERE date_trunc('day', request_date) = '___TODAY' 
  GROUP BY hour
) AS t 
ON s.hour = t.hour
ORDER BY s.hour; 
"""

fmt = '%Y-%m-%d'
d = datetime.datetime.now()
today = d.strftime(fmt)



try:
    
    con_string = "host='" + DBHOST + "' dbname='" + DBNAME + "' user='" + DBUSER + "' password='" + DBPWD + "'"
    con = psycopg2.connect( con_string )
    
    cur = con.cursor()
    
    # today / all maps
    myfilename = join( TMPPATH,  "today_all.csv" )
    with open(myfilename, 'wb') as myfile:
        csv_writer = csv.writer(myfile)
            
    
        cur.execute( sql_day_all.replace( "___TODAY", today ) )
        rows = cur.fetchall()
        for row in rows:
            csv_writer.writerow( row )
    
    hours, impressions = np.loadtxt(myfilename, delimiter=',', unpack=True)

    #plt.bar(hours,  impressions)
    #plt.title("Page impressions on example.com")
    #plt.ylabel("Page impressions")
    #plt.grid(True)
    #plt.show()
    
    fig = plt.figure(figsize=(5,4),dpi=72)
    ax = fig.add_subplot(111)
    plt.title('Today')
    ax.set_ylabel('Maps')
    ax.set_xlabel('Hour')
    ax.bar(hours, impressions, width=1, align='center')
    ax.set_xlim((0,23))
    fig.savefig(join( TMPPATH,  "today_all.png"))

except psycopg2.DatabaseError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value

except IOError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value
    
finally:
    if con:
        con.close()
