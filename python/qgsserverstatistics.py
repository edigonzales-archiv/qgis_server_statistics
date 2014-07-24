#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Name                    : QgsServerStatistics
Description             : Parses an apache access log file and save OWS requests in PostgreSQL database. Creates nvd3 charts.
Date                    : 19/July/2014 
copyright               : (C) 2014 by Stefan Ziegler
email                   : stefan.ziegler.de (at) gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

"""
import sys
import os
import psycopg2
import re
import datetime
import urlparse
import pytz
import collections

from pytz import timezone
from collections import defaultdict, namedtuple
from querybuilder import QueryBuilder
from os.path import join
from json import dumps

'''
Use some logging!
.setLogfile("path"): sets logfile path. Use some default value. Script directory?
'''

class QgsServerStatistics:
    def __init__(self, db_params):
        self.db_host = db_params['db_host']
        self.db_name = db_params['db_name']
        self.db_port = db_params['db_port']
        self.db_schema = db_params['db_schema']
        self.db_table = db_params['db_table']
        self.db_owner = db_params['db_owner']
        self.db_pwd= db_params['db_pwd']
        self.db_user = db_params['db_user']      
              
        self.dst_srs = "21781"
                
        self.con_string = "host='" + self.db_host + "' dbname='" + self.db_name + "' user='" + self.db_owner + "' password='" + self.db_pwd + "'"        
       
    def export_json(self, out_dir, blacklist):
        # Get all maps that were requested.
        try:
            con = psycopg2.connect(self.con_string)
            cur = con.cursor()
                        
            cur = con.cursor() 
            cur.execute("SELECT DISTINCT ON (map) map FROM " + self.db_schema + "." + self.db_table + ";")          
        
            maps = cur.fetchall()
        
        
            # Export json for total requests
            # and every single map.
            if maps:
                # Day
                query_builder = QueryBuilder(blacklist)
                sql = query_builder.get_day("60");
                cur.execute(sql)
                rows = cur.fetchall()
                self.export_data(rows, join(out_dir,  "day_total.json" ), "All Maps",  "#3182bd", True)
                
                for map in maps:
                    sql = query_builder.get_day("60",  str(map[0]));                    
                    cur.execute(sql)
                    rows = cur.fetchall()
                    self.export_data(rows, join(out_dir,  "day_"+str(map[0])+".json" ), str(map[0]),  "#3182bd", True)
                    
                # Week
                sql = query_builder.get_week("60");
                cur.execute(sql)
                rows = cur.fetchall()
                self.export_data(rows, join(out_dir,  "week_total.json" ), "All Maps",  "#3182bd", True)
                
                for map in maps:
                    sql = query_builder.get_week("60",  str(map[0]));                    
                    cur.execute(sql)
                    rows = cur.fetchall()
                    self.export_data(rows, join(out_dir,  "week_"+str(map[0])+".json" ), str(map[0]),  "#3182bd", True)

               # Month
                sql = query_builder.get_month("1800");
                cur.execute(sql)
                rows = cur.fetchall()
                self.export_data(rows, join(out_dir,  "month_total.json" ), "All Maps",  "#3182bd", True)
                
                for map in maps:
                    sql = query_builder.get_month("1800",  str(map[0]));                    
                    cur.execute(sql)
                    rows = cur.fetchall()
                    self.export_data(rows, join(out_dir,  "month_"+str(map[0])+".json" ), str(map[0]),  "#3182bd", True)

               # Year
                sql = query_builder.get_year("7200");
                cur.execute(sql)
                rows = cur.fetchall()
                self.export_data(rows, join(out_dir,  "year_total.json" ), "All Maps",  "#3182bd", True)
                
                for map in maps:
                    sql = query_builder.get_year("7200",  str(map[0]));                    
                    cur.execute(sql)
                    rows = cur.fetchall()
                    self.export_data(rows, join(out_dir,  "year_"+str(map[0])+".json" ), str(map[0]),  "#3182bd", True)

        except psycopg2.Error:
            exc_type, exc_value, exc_traceback = sys.exc_info() 
            print sys.exc_info() 
        
            if con:
                con.rollback()

        finally:
            if con:
                con.close()

    def export_data(self, rows, json_file, key, color, area):
        rowarray_list = []
        for row in rows:
            t = (row[0],  row[1])
            rowarray_list.append(t)

        chart_list = []
        
        d = collections.OrderedDict()
        d['key'] =  key
        d['color'] = color
        d['area'] = area
        d['values'] = rowarray_list
            
        chart_list.append(d)
        
        with open(json_file, "w") as file:
            file.write(dumps(chart_list, file, indent=4))

    def update_database(self, logfile, user_timezone):
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
        
        # I got troubles with the pg queries (interval etc.) when
        # using db table without time zone.
        # What happens when timezone db <> timezone access.log??
        mytimezone = timezone(user_timezone)

        try:
            con = psycopg2.connect(self.con_string)
            cur = con.cursor()
                        
            cur = con.cursor() 
            cur.execute("SELECT max(request_date) FROM " + self.db_schema + "." + self.db_table + ";")          
            res = cur.fetchone()
            
            # figure out max date from database
            if res[0] == None:
                max_date_naive = datetime.datetime.strptime( "1900-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S" )
                max_date = mytimezone.localize(max_date_naive)
                print max_date
            else:
                max_date = res[0]
                print max_date

            with open(logfile) as f:
                for line in f:
                    match = pattern.match(line)
                    if match:
                        res = match.groupdict()
                        request_date_naive = datetime.datetime.strptime( res["time"].split( " " )[0], "%d/%b/%Y:%H:%M:%S" )
                        request_date = mytimezone.localize(request_date_naive)

                        if request_date > max_date:
                            # check if it is a wms request
                            try:
                                req = res["request"].split( " " )[1]
                                qs_params = urlparse.parse_qs( req.split( "?" )[1] )
                                
                                wms = req.split( "/" )[1]
                                if wms == "wms":
                                    ip = res["host"]
                                    request_url = line
                                    referer = res["referer"]
                                    user_agent = res["user_agent"]
                
                                    map = (req.split( "/" )[2]).split( "?" )[0]
                                    # Some requests do have two forward slashes. 
                                    # Regex (re.split()) would be nicer, though...
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
                                    
                                    # If wms request is not in our standard srs we need to transform it.
                                    src_srs = crs[0].split(":")[1]
                                    bbox_geom_string = "SELECT ST_AsText(ST_Transform(ST_MakeEnvelope(" + bbox[0] + ", " + src_srs + "),"+self.dst_srs+"));"

                                    # Escape single quoates with dollar bla bla bla.
                                    insert_string = "INSERT INTO " + self.db_schema + "." + self.db_table + "(ip, request_date, request_url, referer, user_agent, map, layers, format, dpi, version, service, request, crs, bbox, bbox_geom, width, height) VALUES ('" + ip + "', '" + str(request_date) + "', $esc$" + request_url + "$esc$, '" + referer + "', '" + user_agent + "', '" + map + "', $esc$" + layers[0] + "$esc$, '" + format[0] + "', '" + dpi[0] + "', '" +  version[0] + "', '" + service[0] + "', '" + request[0] + "', '" + crs[0] + "', '" + bbox[0] + "', ST_Transform(ST_MakeEnvelope(" + bbox[0] + ", " + src_srs + "),"+self.dst_srs+"), " + width[0] + ", " + height[0]  + ");"
                                    
                                    cur.execute(insert_string)
                                
                            except IndexError:
                                exc_type, exc_value, exc_traceback = sys.exc_info() 
                            except KeyError:
                                exc_type, exc_value, exc_traceback = sys.exc_info() 
                            
            con.commit()
        
        except psycopg2.Error:
            exc_type, exc_value, exc_traceback = sys.exc_info() 
            print sys.exc_info() 
        
            if con:
                con.rollback()

        finally:
            if con:
                con.close()


        
    def create_sql(self, out_file):
        sql = "CREATE SCHEMA " + self.db_schema + " AUTHORIZATION " + self.db_owner + ";\n"
        sql += "GRANT ALL ON SCHEMA " + self.db_schema + " TO " + self.db_owner + ";\n"
        sql += "GRANT USAGE ON SCHEMA " + self.db_schema + " TO " + self.db_user + ";\n\n"

        sql += "CREATE TABLE " + self.db_schema + "." + self.db_table
        sql += """
(
  ogc_fid serial NOT NULL,
  ip inet,
  request_date timestamp with time zone,
  request_url varchar,
  referer varchar,
  user_agent varchar,
  map varchar,
  layers varchar,
  format varchar,
  dpi varchar,
  version varchar,
  service varchar,
  request varchar,
  styles varchar,
  crs varchar,
  bbox varchar,
  bbox_geom geometry,
  --bbox_geom geometry(Polygon, """ + self.dst_srs + """),
  width double precision,
  height double precision,
  CONSTRAINT wms_requests_pkey PRIMARY KEY (ogc_fid),
  CONSTRAINT enforce_srid_bbox_geom CHECK (st_srid(bbox_geom) = 21781)
)
WITH (
  OIDS=FALSE
);
"""
        
        sql += "ALTER TABLE " + self.db_schema + "." + self.db_table + " OWNER TO " + self.db_owner + ";\n";
        sql += "GRANT ALL ON TABLE " + self.db_schema + "." + self.db_table + " TO " + self.db_owner + ";\n";
        sql += "GRANT SELECT ON TABLE " + self.db_schema + "." + self.db_table + " TO " + self.db_user + ";\n\n";
        
        sql += "CREATE INDEX idx_" + self.db_table + "_bbox_geom\n"
        sql += "  ON " + self.db_schema + "." + self.db_table + "\n"
        sql += "  USING gist\n"
        sql += "  (bbox_geom);\n\n"

        sql += "CREATE INDEX idx_" + self.db_table + "_requests_date\n"
        sql += "  ON " + self.db_schema + "." + self.db_table + "\n"
        sql += "  USING btree\n"
        sql += "  (request_date);\n\n"

        sql += "CREATE INDEX idx_" + self.db_table + "_map\n"
        sql += "  ON " + self.db_schema + "." + self.db_table + "\n"
        sql += "  USING btree\n"
        sql += "  (map);\n\n"

        sql += "INSERT INTO geometry_columns VALUES (\'\', \'" + self.db_schema + "\', \'" + self.db_table + "\', bbox_geom, 2, \'" + self.dst_srs + "\', \'POLYGON\');" 

        with open(out_file, "w") as text_file:
            text_file.write(sql)
        
    def set_srs(self, srs):
        self.srs = srs
