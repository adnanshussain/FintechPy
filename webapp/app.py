from flask import Flask
import flask_login
from .sqlalchemy_models import DbSession, User
from . import config
from .pp_blueprint import *
from .api_blueprint import *

######################
### Create the App ###
######################
theapp = Flask(__name__)
theapp.config.from_object(config)

###############################
### Initialize flask-login  ###
###############################
login_manager = flask_login.LoginManager()
login_manager.init_app(theapp)

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
    return DbSession().query(User).get(user_id)

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
