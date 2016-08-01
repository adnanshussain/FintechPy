import datetime, os
import sqlite3
import webapp.config as config

###############################
### User Defined Functions  ###
###############################
def _udf_change_percentage(y1, y2):
    return ((y2 - y1) / y1) * 100

def _udf_day_of_week_name(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    return datetime.date(year, month, day).strftime("%A")

def _udf_day_of_week(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    return int(datetime.date(year, month, day).strftime("%w"))

###############################
###  Generic DB Functions   ###
###############################
def _get_open_db_connection(use_row_factory=True, register_udfs=False):
    conn = sqlite3.connect(config.configs[os.getenv(config.ENVAR_FINTECH_CONFIG)].NEW_DB_PATH)

    if use_row_factory:
        conn.row_factory = sqlite3.Row

    if register_udfs:
        _register_udfs(conn)

    return conn

def _close_db_connection(conn):
    conn.close()

def _register_udfs(conn):
    conn.create_function("cp", 2, _udf_change_percentage)
    conn.create_function("dow_name", 1, _udf_day_of_week_name)
    conn.create_function("dow", 1, _udf_day_of_week)
    return conn

###############################
### General Query Functions ###
###############################
def _fetch_all(sql, *args):
    conn = _get_open_db_connection(use_row_factory=True)
    c = conn.execute(sql, *args) # TODO: Need to understand how this *args really works
    result = c.fetchall()
    _close_db_connection(conn)
    return result
