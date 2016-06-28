from flask import Flask
from . import config
from .publicwebsite_blueprint import *
from .api_blueprint import *

######################
### Create the App ###
######################
theapp = Flask(__name__)
# theapp.json_encoder = config.NonASCIIJSONEncoder

theapp.config.from_object(config)

###############################
### Register Blueprints     ###
###############################
theapp.register_blueprint(publicweb_bp)
theapp.register_blueprint(api_bp)


