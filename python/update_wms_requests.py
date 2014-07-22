#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import psycopg2
import re
import datetime
import pytz
from pytz import timezone
import urlparse
import logging
import logging.handlers
from collections import defaultdict, namedtuple

LOG_FILE = os.path.dirname(os.path.realpath(__file__)) + '/log_update_wms_requests.log'

# VARS
DBHOST = "localhost"
DBPORT = "5432"
DBNAME = "rosebud2"
DBUSER = "stefan"
DBPWD = "ziegler12"

DBSCHEMA_STATS = "sogis_ows_statistics"
DBTABLE_WMS_REQUESTS = "wms_requests"

DST_SRS = "21781"

ACCESS_LOG = "/home/stefan/Projekte/qgis_server_statistics/data/sogis/access.log"

# logging
logger = logging.getLogger('LogQGIS_SERVER_WMS_REQUESTS')  
logger.setLevel(logging.DEBUG)
log_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=4)  
log_handler.setFormatter(logging.Formatter('%(levelname)s: %(asctime)s %(message)s'))
logger.addHandler(log_handler)

logger.debug('')
logger.debug('-----------------')
logger.debug('Skript gestarted:')
logger.debug('-----------------')
logger.debug('')

# apache logfile pattern
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

# Timezone...
# Testen, ob noch alles funktioniert. 
# Grund für den Wechsel "with time zone" war PostgreSQL.
# Da gab das Hin- und Herrechnen mit EPOCH komische Resultate.
mytimezone = timezone('Europe/Amsterdam')

con = None

try:
    
    con_string = "host='" + DBHOST + "' dbname='" + DBNAME + "' user='" + DBUSER + "' password='" + DBPWD + "'"
    con = psycopg2.connect( con_string )
    
    cur = con.cursor() 
    cur.execute("SELECT max(request_date) FROM " + DBSCHEMA_STATS + "." + DBTABLE_WMS_REQUESTS + ";")          
    res = cur.fetchone()
    
    # figure out max date from database
    if res[0] == None:
        max_date_naive = datetime.datetime.strptime( "1900-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S" )
        max_date = mytimezone.localize(max_date_naive)
        print max_date
    else:
        max_date = res[0]
        print max_date

    logger.debug("Max date: " + str(max_date))

    # loop tĥrough ACCESS_LOG
    with open( ACCESS_LOG ) as f:
        for line in f:
            #print line
            match = pattern.match(line)
            if match:
                res = match.groupdict()
#                print res["time"]
                request_date_naive = datetime.datetime.strptime( res["time"].split( " " )[0], "%d/%b/%Y:%H:%M:%S" )
                request_date = mytimezone.localize(request_date_naive)

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
                            
                            ## GetProjectSettings-Aufrufe könnte vielleicht verwendet werden, um "Besucher" zu zählen?
            
                            ip = res["host"]
                            request_url = line
                            referer = res["referer"]
                            user_agent = res["user_agent"]
        
                            map = (req.split( "/" )[2]).split( "?" )[0]
                            # Einige Requests haben zwei forward slashes. (regex waere sicher schoener... (re.split).
                            if map == "":
                                map = (req.split( "/" )[3]).split( "?" )[0]
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

                            # Single quotes werden escaped .
                            insert_string = "INSERT INTO " + DBSCHEMA_STATS + "." + DBTABLE_WMS_REQUESTS + "(ip, request_date, request_url, referer, user_agent, map, layers, format, dpi, version, service, request, crs, bbox, bbox_geom, width, height) VALUES ('" + ip + "', '" + str(request_date) + "', $esc$" + request_url + "$esc$, '" + referer + "', '" + user_agent + "', '" + map + "', $esc$" + layers[0] + "$esc$, '" + format[0] + "', '" + dpi[0] + "', '" +  version[0] + "', '" + service[0] + "', '" + request[0] + "', '" + crs[0] + "', '" + bbox[0] + "', ST_Transform(ST_MakeEnvelope(" + bbox[0] + ", " + src_srs + "),"+DST_SRS+"), " + width[0] + ", " + height[0]  + ");"
#                            logger.debug(insert_string);
                            
                            cur.execute( insert_string )
                        
                    except IndexError:
                        exc_type, exc_value, exc_traceback = sys.exc_info() 
                    except KeyError:
                        exc_type, exc_value, exc_traceback = sys.exc_info() 
                    
    con.commit()
    logger.debug("WMS requests committed to database.")

except psycopg2.DatabaseError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value
    logger.error(exc_value)
            
except IOError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print exc_value
    logger.error(exc_value)

finally:
    if con:
        con.close()
        logger.debug("Database connection closed.")

        logger.debug('')
        logger.debug('---------------')
        logger.debug('Skript beendet:')
        logger.debug('---------------')
        logger.debug('')
