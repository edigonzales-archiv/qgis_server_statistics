#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
from qgsserverstatistics import QgsServerStatistics

db_params = {}
db_params['db_host'] = 'localhost'
db_params['db_name'] =  'rosebud2'
db_params['db_port'] =  '5432'
db_params['db_schema'] =  'sogis_ows_statistics'
db_params['db_table'] =  'wms_requests'
db_params['db_owner'] =  'stefan'
db_params['db_pwd'] =  'ziegler12'
db_params['db_user'] =  'mspublic'

blacklist = {}
blacklist['map'] = ['strassenkarte',  'grundbuchplan']
blacklist['ip'] = ['193.135.67.105/32', '144.76.82.106/32']
#blacklist['referer'] = ...
# -> something like WHERE ... ... AND ip NOT IN [..., ..., ...] etc. etc.
# NOT YET IMPLEMENTED.

statistics = QgsServerStatistics(db_params)
statistics.set_srs("21781")
#statistics.create_sql("/home/stefan/tmp/statistics.sql")
statistics.update_database('/home/stefan/Projekte/qgis_server_statistics/data/catais/access.log', 'Europe/Amsterdam')
statistics.export_json('/home/stefan/Projekte/qgis_server_statistics/html/bootstrap/data/', blacklist)
    
    
