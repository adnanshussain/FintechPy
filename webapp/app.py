import flask_login
from . import theapp, db

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



