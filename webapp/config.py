import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))

class ConfigBase:
    ###############################
    ### Custom Configs          ###
    ###############################
    _OLD_DB_NAME = 'argaam_fintech.db'
    _NEW_DB_NAME = 'fintech.db'
    OLD_DB_PATH = os.path.join(basedir, 'data', _OLD_DB_NAME)
    NEW_DB_PATH = os.path.join(basedir, 'data', _NEW_DB_NAME)
    SQL_ALCHEMY_DB_URL = "sqlite:///" + NEW_DB_PATH
    # This config is used specifically by flask_sqlalchemy
    SQLALCHEMY_DATABASE_URI = SQL_ALCHEMY_DB_URL

    ###############################
    ### Flask Configs           ###
    ###############################
    SECRET_KEY = "secret key for session usage"

    ARGAAM_MSSQL_SERVER_IP = '172.16.3.65'
    ARGAAM_MSSQL_DB_NAME = 'ArgaamPlus'
    ARGAAM_MSSQL_DB_USER_NAME = 'argaamplususer'
    ARGAAM_MSSQL_DB_PWD = 'argplus123$'
    ARGAAM_MSSQL_CONN_STR = 'Driver={SQL Server Native Client 11.0};Server=%s;Database=%s;Uid=%s;Pwd=%s;' \
                            % (ARGAAM_MSSQL_SERVER_IP, ARGAAM_MSSQL_DB_NAME, ARGAAM_MSSQL_DB_USER_NAME, \
                               ARGAAM_MSSQL_DB_PWD)

class DevConfig(ConfigBase):
    HOST = "0.0.0.0"
    # HOST = None
    PORT = 5001
    DEBUG = True
    #TEMPLATES_AUTO_RELOAD = True
    #EXPLAIN_TEMPLATE_LOADING = True

class ProdConfig(ConfigBase):
    ARGAAM_MSSQL_SERVER_IP = '172.16.3.65'
    ARGAAM_MSSQL_DB_NAME = 'ArgaamPlus'
    ARGAAM_MSSQL_DB_USER_NAME = 'argaamplususer'
    ARGAAM_MSSQL_DB_PWD = 'argplus123$'
    ARGAAM_MSSQL_CONN_STR = 'Driver={SQL Server Native Client 11.0};Server=%s;Database=%s;Uid=%s;Pwd=%s;' \
                            % (ARGAAM_MSSQL_SERVER_IP, ARGAAM_MSSQL_DB_NAME, ARGAAM_MSSQL_DB_USER_NAME, \
                               ARGAAM_MSSQL_DB_PWD)

configs = {
    'Dev': DevConfig(),
    'Prod': ProdConfig()
}

ENVAR_FINTECH_CONFIG = 'FINTECH_CONFIG'