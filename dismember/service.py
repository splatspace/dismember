from flask.ext.peewee.admin import Admin
from flask.ext.peewee.auth import Auth

import os
from flask import Flask
from itsdangerous import URLSafeTimedSerializer
from flask_peewee.db import Database


FLASK_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Don't import any modules that use DB models up here, because they need to
# import and use the "db" object from this module (which would not be initialized
# yet).  Instead, import them as requred after db has been initialized.  This
# file is the only file that requires this special treatment.  Other files can
# import and use models freely.

app = Flask(__name__)

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

    # Import the views to enable Flask handlers
    import dismember.views

    app.run(host=config['flask']['bind'], debug=config['flask']['debug'])