import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))

###############################
### Custom Configs          ###
###############################
DB_PATH = os.path.join(basedir, 'data/argaam_fintech.db')
HOST = "0.0.0.0" # None

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