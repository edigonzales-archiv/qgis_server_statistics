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

#blacklist = {}
#blacklist['map'] = ['strassenkarte',  'grundbuchplan']
#blacklist['ip'] = ...
#blacklist['referer'] = ...
# -> something like WHERE map NOT IN [..., ..., ...] etc. etc.


try:
    statistics = QgsServerStatistics(db_params)
    statistics.init_database()
    
    
    
    
    

except KeyError:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print sys.exc_info() 
except Exception:
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    print sys.exc_info() 

