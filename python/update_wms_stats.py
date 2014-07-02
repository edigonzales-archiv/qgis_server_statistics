#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import psycopg2
import re
import datetime
import urlparse
from collections import defaultdict, namedtuple

DBHOST = "localhost"
DBPORT = "5432"
DBNAME = "rosebud2"
DBUSER = "stefan"
DBPWD = "ziegler12"

DB_STATS_SCHEMA = "qgis_server_statistics"
WMS_STATS_TABLE = "wms_stats"

DST_SRS = "21781"

LOGFILE = "/home/catais/catais.org/log/access.log"

pattern = re.compile( 
    r"(?P<host>[\d\.]+)\s" 
    r"(?P<identity>\S*)\s" 
    r"(?P<user>\S*)\s"
    r"\[(?P<time>.*?)\]\s"
    r'"(?P<request>.*?)"\s'
    r"(?P<status>\d+)\s"
    r"(?P<bytes>\S*)\s"
    r'"(?P<referer>.*?)"\s' # [SIC]
    r'"(?P<user_agent>.*?)"\s*' 
)

con = None

try:
    
    con_string = "host='" + DBHOST + "' dbname='" + DBNAME + "' user='" + DBUSER + "' password='" + DBPWD + "'"
    con = psycopg2.connect( con_string )
    
    cur = con.cursor() 
    cur.execute("SELECT max(request_date) FROM " + DB_STATS_SCHEMA + "." + WMS_STATS_TABLE + ";")          
    res = cur.fetchone()
    
    # figure out max date from database
    if res[0] == None:
        max_date = datetime.datetime.strptime( "1900-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S" )
        print max_date
    else:
        max_date = res[0]
        print max_date

    # loop tĥrough logfile
    with open( LOGFILE ) as f:
        for line in f:
            #print line
            match = pattern.match(line)
            if match:
                res = match.groupdict()
                print res["time"]
                request_date = datetime.datetime.strptime( res["time"].split( " " )[0], "%d/%b/%Y:%H:%M:%S" )
                #print request_date
                if request_date > max_date:
                    # check if it is a wms request
                    try:
                        req = res["request"].split( " " )[1]
                        #print req
                        qs_params = urlparse.parse_qs( req.split( "?" )[1] )
                        
                        wms = req.split( "/" )[1]
                        #print wms
                        if wms == "wms":
                            
                            ## GetProjectSettings könnte vielleicht verwendet werden, um Besucher zu zählen?
            
                            ip = res["host"]
                            request_url = line
                            referer = res["referer"]
                            user_agent = res["user_agent"]
        
                            map = (req.split( "/" )[2]).split( "?" )[0]
                            layers = qs_params["LAYERS"]
                            format = qs_params["FORMAT"]
                            dpi = qs_params["DPI"]
                            version = qs_params["VERSION"]
                            service = qs_params["SERVICE"]
                            request = qs_params["REQUEST"]
                            layers = qs_params["LAYERS"]
                            #styles = qs_params["STYLES"]
                            crs = qs_params["CRS"]
                            bbox = qs_params["BBOX"]
                            width = qs_params["WIDTH"]
                            height = qs_params["HEIGHT"]
                            
                            ## Falls wms-request nicht in epsg:21781 gemacht wird, muss umprojiziert werden.
                            src_srs = crs[0].split(":")[1]
                            bbox_geom_string = "SELECT ST_AsText(ST_Transform(ST_MakeEnvelope(" + bbox[0] + ", " + src_srs + "),"+DST_SRS+"));"

                            insert_string = "INSERT INTO " + DB_STATS_SCHEMA + "." + WMS_STATS_TABLE + "(ip, request_date, request_url, referer, user_agent, map, layers, format, dpi, version, service, request, crs, bbox, bbox_geom, width, height) VALUES ('" + ip + "', '" + str(request_date) + "', '" + request_url + "', '" + referer + "', '" + user_agent + "', '" + map + "', '" + layers[0] + "', '" + format[0] + "', '" + dpi[0] + "', '" +  version[0] + "', '" + service[0] + "', '" + request[0] + "', '" + crs[0] + "', '" + bbox[0] + "', ST_Transform(ST_MakeEnvelope(" + bbox[0] + ", " + src_srs + "),"+DST_SRS+"), " + width[0] + ", " + height[0]  + ");"
                            cur.execute( insert_string )
                        
                    except IndexError:
                        exc_type, exc_value, exc_traceback = sys.exc_info() 
                        #print exc_value
                    except KeyError:
                        exc_type, exc_value, exc_traceback = sys.exc_info() 
                        #print exc_value

                    
    con.commit()

except psycopg2.DatabaseError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value
            
except IOError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value
    
finally:
    if con:
        con.close()
