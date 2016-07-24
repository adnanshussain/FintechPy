import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))

###############################
### Custom Configs          ###
###############################
_OLD_DB_NAME = 'argaam_fintech.db'
_NEW_DB_NAME = 'fintech.db'
OLD_DB_PATH = os.path.join(basedir, 'data', _OLD_DB_NAME)
NEW_DB_PATH = os.path.join(basedir, 'data', _NEW_DB_NAME)
SQL_ALCHEMY_DB_URL = "sqlite:///" + NEW_DB_PATH

# HOST = "0.0.0.0"
HOST = None
PORT = 5001

_ARGAAM_MSSQL_SERVER_IP = '172.16.3.65'
_ARGAAM_MSSQL_DB_NAME = 'ArgaamPlus'
_ARGAAM_MSSQL_DB_USER_NAME = 'argaamplususer'
_ARGAAM_MSSQL_DB_PWD = 'argplus123$'
ARGAAM_MSSQL_CONN_STR = 'Driver={SQL Server Native Client 11.0};Server=%s;Database=%s;Uid=%s;Pwd=%s;' \
                        % (_ARGAAM_MSSQL_SERVER_IP, _ARGAAM_MSSQL_DB_NAME, _ARGAAM_MSSQL_DB_USER_NAME, \
                           _ARGAAM_MSSQL_DB_PWD)

###############################
### Flask Configs           ###
###############################
SECRET_KEY = "secret key for session usage"

#TEMPLATES_AUTO_RELOAD = True

DEBUG = True
#EXPLAIN_TEMPLATE_LOADING = True

# Not in use anymore...
class NonASCIIJSONEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        super(NonASCIIJSONEncoder, self).__init__(**kwargs)
