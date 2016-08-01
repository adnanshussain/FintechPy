import os
import flask_login
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from webapp import config

######################
### Create the App ###
######################
theapp = Flask(__name__)
theapp.config.from_object(config.configs[os.getenv(config.ENVAR_FINTECH_CONFIG)])

db = SQLAlchemy(theapp)

from webapp import pp_blueprint
from .api_blueprint import *
from webapp.data_access.sqlalchemy_models import User

###############################
### Initialize flask-login  ###
###############################
login_manager = flask_login.LoginManager()
login_manager.init_app(theapp)

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

###############################
### Initialize CP           ###
###############################
from . import controlpanel

###############################
### Register Blueprints     ###
###############################
theapp.register_blueprint(pp_blueprint.publicweb_bp)
theapp.register_blueprint(api_bp)

###############################
### Configure Loggings      ###
###############################
if not theapp.debug:
    pass
    # import logging
    # from logging.handlers import SMTPHandler
    #
    # credentials = None
    #
    # if MAIL_USERNAME or MAIL_PASSWORD:
    #     credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    #
    # mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    # mail_handler.setLevel(logging.ERROR)
    # flaskApp.logger.addHandler(mail_handler)

# if not flaskApp.debug:
#     import logging
#     from logging.handlers import RotatingFileHandler
#
#     file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
#     file_handler.setFormatter(
#         logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#     file_handler.setLevel(logging.INFO)
#     flaskApp.logger.addHandler(file_handler)
#
#     flaskApp.logger.setLevel(logging.INFO)
#     flaskApp.logger.info('microblog startup')

# theapp.json_encoder = config.NonASCIIJSONEncoder
# theapp.jinja_env.line_statement_prefix = '#'


