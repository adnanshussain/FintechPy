import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))

###############################
### Custom Configs          ###
###############################
__OLD_DB_NAME = 'argaam_fintech.db'
__NEW_DB_NAME = 'fintech.db'
OLD_DB_PATH = os.path.join(basedir, 'data', __OLD_DB_NAME)
NEW_DB_PATH = os.path.join(basedir, 'data', __NEW_DB_NAME)
SQL_ALCHEMY_DB_URL = "sqlite:///" + NEW_DB_PATH

HOST = None # "0.0.0.0"

# Not in use anymore...
class NonASCIIJSONEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        super(NonASCIIJSONEncoder, self).__init__(**kwargs)

###############################
### Flask Configs           ###
###############################
SECRET_KEY = "need to put a more secure key"




#TEMPLATES_AUTO_RELOAD = True

DEBUG = True
#EXPLAIN_TEMPLATE_LOADING = True