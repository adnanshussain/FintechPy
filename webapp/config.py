import os
import configparser

basedir = os.path.abspath(os.path.dirname(__file__))
config_ini = configparser.ConfigParser()
config_ini.read(basedir + '\\config.ini')

class _ConfigBase:
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

    ARGAAM_MSSQL_SERVER_IP = config_ini['ARGAAMPLUS QA']['SERVER_IP']
    ARGAAM_MSSQL_DB_NAME = config_ini['ARGAAMPLUS QA']['DB_NAME']
    ARGAAM_MSSQL_DB_USER_NAME = config_ini['ARGAAMPLUS QA']['USER_NAME']
    ARGAAM_MSSQL_DB_PWD = config_ini['ARGAAMPLUS QA']['PWD']

class _DevConfig(_ConfigBase):
    HOST = "0.0.0.0"
    # HOST = None
    PORT = 5001
    DEBUG = True
    #TEMPLATES_AUTO_RELOAD = True
    #EXPLAIN_TEMPLATE_LOADING = True

class _ProdConfig(_ConfigBase):
    ARGAAM_MSSQL_SERVER_IP = '172.16.3.65'
    ARGAAM_MSSQL_DB_NAME = 'ArgaamPlus'
    ARGAAM_MSSQL_DB_USER_NAME = 'argaamplususer'
    ARGAAM_MSSQL_DB_PWD = 'argplus123$'
    ARGAAM_MSSQL_CONN_STR = 'Driver={SQL Server Native Client 11.0};Server=%s;Database=%s;Uid=%s;Pwd=%s;' \
                            % (ARGAAM_MSSQL_SERVER_IP, ARGAAM_MSSQL_DB_NAME, ARGAAM_MSSQL_DB_USER_NAME, \
                               ARGAAM_MSSQL_DB_PWD)

_configs = {
    'Dev': _DevConfig(),
    'Prod': _ProdConfig()
}

_ENVAR_FINTECH_CONFIG = 'FINTECH_CONFIG'

active_config = _configs[os.getenv(_ENVAR_FINTECH_CONFIG)]