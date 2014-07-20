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

 sys.exit(3) = UNKNOWN
 sys.exit(2) = ERROR
 sys.exit(1) = WARNING
 sys.exit(0) = OK

"""
import sys
import os
import psycopg2
import re
import datetime
import pytz

from pytz import timezone
from collections import defaultdict, namedtuple


class QgsServerStatistics:
    def __init__(self, db_params, ):
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
        
    def init_database(self):
        try:
            con = psycopg2.connect(self.con_string)
            cur = con.cursor()
            
            cur.execute("CREATE SCHEMA " + self.db_schema + " AUTHORIZATION " + self.db_owner + ";")
            cur.execute("GRANT ALL ON SCHEMA " + self.db_schema + " TO " + self.db_owner + ";")
            cur.execute("GRANT USAGE ON SCHEMA " + self.db_schema + " TO " + self.db_user + ";")
            
            con.commit()

        except psycopg2.Error:
            exc_type, exc_value, exc_traceback = sys.exc_info() 
            print sys.exc_info() 
        
            if con:
                con.rollback()

        finally:
            if con:
                con.close()
        
        
    def set_srs(self, srs):
        self.srs = srs
