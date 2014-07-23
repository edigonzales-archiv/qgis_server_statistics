#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Name                    : QueryBuilder
Description             : fubar.
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

class QueryBuilder:    
    def __init__(self, the_blacklist):
        self.blacklist = the_blacklist
        self.fixed_interval = 60
        
    def get_day(self, request_interval, map = None):
        return self.get_sql(request_interval, "1 day", map)
       
    def get_week(self, request_interval, map = None):
        return self.get_sql(request_interval, "1 week", map)

    def get_month(self, request_interval, map = None):
        return self.get_sql(request_interval, "1 month", map)

    def get_year(self, request_interval, map = None):
        return self.get_sql(request_interval, "1 year", map)

    def get_sql(self, request_interval, log_interval, map):
        sql = """
SELECT t1.my_datetime * """ + request_interval + """ * 1000, coalesce(t2.count / """ + str(int(request_interval) / self.fixed_interval) + """, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / """ + request_interval + """) as my_datetime
 FROM generate_series(NOW() - '"""+ log_interval +"""'::INTERVAL, NOW(), '""" + request_interval + """sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / """ + request_interval + """) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / """ + request_interval + """) * """ + request_interval + """ * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '"""+ log_interval +"""'::INTERVAL
 """
        if map != None:
            sql += "AND map = '" + map + "'"
            
        sql += """
 GROUP BY round(extract('epoch' from request_date) / """ + request_interval + """)
 ORDER BY round(extract('epoch' from request_date) / """ + request_interval + """)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;
"""   
        return sql
        
