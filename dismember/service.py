from flask.ext.peewee.admin import Admin
from flask.ext.peewee.auth import Auth

import os
from flask import Flask
from flask.ext.assets import Environment
from itsdangerous import URLSafeTimedSerializer
from flask_peewee.db import Database


FLASK_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Don't import any modules that use DB models up here; import them as required
# but after db.configure_db has been executed.  This file is the only file that
# requires this special treatment.  Other files can import and use models freely.

app = Flask(__name__)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = '/members/login'

# Loaded by run
base = None
config = None
db = None
user_datastore = None
auth = None
admin = None
cookie_serializer = None


@app.before_first_request
def create_builtins():
    global config, db, user_datastore

    from dismember.models.user import User
    from dismember.models.role import Role
    from dismember.models.user_role import UserRole

    # Create builtin roles
    for builtin_role in config['builtins']['roles']:
        if not Role.select(Role.name == builtin_role['name']).exists():
            Role.create(**builtin_role)

    # Create builtin users (and find related roles)
    user_role = []
    for builtin_user in config['builtins']['users']:
        if not User.select(User.username == builtin_user['username']).exists():
            user = User(**builtin_user)
            user.set_password(user.password)
            user.enabled = True

            # Remember ther user ID and each role assigned
            for role_name in builtin_user['role_names']:
                role = Role.get(Role.name == role_name)
                user_role.append((user, role))

            user.save()

    # Map users to roles
    for (user, role) in user_role:
        UserRole.create(user=user, role=role)


def run(the_config):
    global base, app, config, db, admin, user_datastore, auth, cookie_serializer
    config = the_config

    app.secret_key = config['flask']['session_secret_key']

    # Cookie serializer
    cookie_serializer = URLSafeTimedSerializer(app.secret_key)

    # Flask-Peewee
    app.config['DATABASE'] = config['db']
    db = Database(app)
    # Import all models (creates required tables if needed)
    import dismember.models

    auth = Auth(app, db, user_model=dismember.models.user.User)
    admin = Admin(app, auth)
    import dismember.admin

    admin.setup()

    # Configure Flask-Mail
    # mail = Mail(app)
    # app.mail = mail

    # Flask-Security Core
    # app.config['SECURITY_URL_PREFIX'] = '/security'
    # app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    # app.config['SECURITY_PASSWORD_SALT'] = config['flask']['password_salt']

    # Flask-Security Feature Flags
    # app.config['SECURITY_CONFIRMABLE'] = True
    # app.config['SECURITY_REGISTERABLE'] = True
    # app.config['SECURITY_RECOVERABLE'] = True
    # app.config['SECURITY_TRACKABLE'] = True
    # app.config['SECURITY_CHANGEABLE'] = True

    # Flask-Login
    # app.config['REMEMBER_COOKIE_DURATION'] = config['flask']['remember_me_cookie_duration']

    # Flask-Email
    # app.config['MAIL_SERVER'] = 'localhost'
    # app.config['MAIL_PORT'] = 25
    # app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_USERNAME'] = 'username'
    # app.config['MAIL_PASSWORD'] = 'password'

    # Flask-Security Core
    #user_datastore = SQLAlchemyUserDatastore(db, dismember.models.user.User, dismember.models.role.Role)
    #security = Security(app, user_datastore)

    # Flask-Admin
    # admin = Admin(app, name=config['site']['name'])

    # Flask-Assets
    assets = Environment(app)
    assets_output_dir = os.path.join(FLASK_APP_DIR, 'static', 'gen')
    if not os.path.exists(assets_output_dir):
        os.mkdir(assets_output_dir)

    # Import the views to enable Flask handlers
    import dismember.views

    app.run(host=config['flask']['bind'], debug=config['flask']['debug'])