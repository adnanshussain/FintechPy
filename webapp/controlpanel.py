from flask import redirect, url_for, request, abort
from flask_admin import Admin, expose, helpers, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import flask_login
from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash
from .sqlalchemy_models import DbSession, User, EventCategory
from .app import theapp

# Define login form (for flask-login)
class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_email(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        # if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return DbSession().query(User).filter_by(email=self.email.data).first()

# Create customized model view class
class AdminModelView(ModelView):

    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    form_excluded_columns = ['created_by_id', 'created_on', 'modified_by_id', 'modified_on']


# Create customized index view class that handles login & registration
class FintechAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            url = url_for('.login_view')
            return redirect(url)
        return super(FintechAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            flask_login.login_user(user)

        if flask_login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        # link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        # self._template_args['link'] = link
        return super(FintechAdminIndexView, self).index()
        # return self.render("admin/login.html")

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(FintechAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        flask_login.logout_user()
        return redirect(url_for('.index'))

class UserModelView(AdminModelView):
    can_view_details = True
    column_searchable_list = ['email']
    column_filters = ['email']

class EventCategoryModelView(AdminModelView):
    can_view_details = True
    form_edit_rules = form_create_rules = ('name_en', 'name_ar', 'is_subcategory', 'parent')

##################################
### Create the Admin Interface ###
##################################
admin = Admin(theapp, name='Fintech CP', index_view=FintechAdminIndexView(), base_template='admin/my_master.html', template_mode='bootstrap3')

###############################
### Add the ModelViews      ###
###############################
admin.add_view(UserModelView(User, DbSession()))
admin.add_view(EventCategoryModelView(EventCategory, DbSession()))

