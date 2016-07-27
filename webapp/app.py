from flask import Flask
import flask_login
from flask_sqlalchemy import SQLAlchemy
# from .sqlalchemy_models import DbSession, User
from . import config

######################
### Create the App ###
######################
theapp = Flask(__name__)
theapp.config.from_object(config)

db = SQLAlchemy(theapp)

from .pp_blueprint import *
from .api_blueprint import *
from . import sqlalchemy_models

###############################
### Initialize flask-login  ###
###############################
login_manager = flask_login.LoginManager()
login_manager.init_app(theapp)

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(sqlalchemy_models.User).get(user_id)

###############################
### Initialize CP           ###
###############################
import webapp.controlpanel

###############################
### Register Blueprints     ###
###############################
theapp.register_blueprint(publicweb_bp)
theapp.register_blueprint(api_bp)

# theapp.json_encoder = config.NonASCIIJSONEncoder
# theapp.jinja_env.line_statement_prefix = '#'
