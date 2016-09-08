# good place to put any package-level initialisation code

# Depending on what you plan to do it's a good place to import public stuff from the modules in your package so
# people can simply use from yourpackage import whatever instead of
# having to use from yourpackage.somemodule import whatever.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import active_config

######################
### Create the App ###
######################
theapp = Flask(__name__)
theapp.config.from_object(active_config)

db = SQLAlchemy(theapp)

from . import pp_blueprint, api_blueprint

###############################
### Register Blueprints     ###
###############################
theapp.register_blueprint(pp_blueprint.publicweb_bp)
theapp.register_blueprint(api_blueprint.api_bp)

###############################
### Initialize CP           ###
###############################
from . import controlpanel

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
