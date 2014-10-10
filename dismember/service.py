from flask import Flask
from flask.ext.peewee.admin import Admin
from flask.ext.peewee.auth import Auth
from flask.ext.peewee.rest import RestAPI, AdminAuthentication
from flask.ext.security import PeeweeUserDatastore, Security
from flask_peewee.db import Database

# Don't import any modules that use DB models up here, because they need to
# import and use the "db" object from this module (which would not be initialized
# yet).  Instead, import them as requred after db has been initialized.  This
# file is the only file that requires this special treatment.  Other files can
# import and use models freely.

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('dismember.config')
# Read the local "./instance/config.py" if it exists
app.config.from_pyfile('config.py', silent=True)

# Initialized by run
db = None
auth = None
admin = None
api = None


def run():
    global app, db, admin, auth, api

    # Flask-Peewee
    db = Database(app)

    # Importing models creates tables (if required)
    import dismember.models
    from dismember.models.user import User, UserAdmin
    from dismember.models.role import Role
    from dismember.models.user_role import UserRole
    from dismember.models.member_status import MemberStatus, MemberStatusAdmin
    from dismember.models.member_type import MemberType, MemberTypeAdmin

    # Setup Flask-Security
    user_datastore = PeeweeUserDatastore(db, User, Role, UserRole)
    security = Security(app, user_datastore)

    # Flask-Peewee
    auth = Auth(app, db, user_model=dismember.models.user.User)
    admin = Admin(app, auth, branding=app.config['DISMEMBER_SITE_NAME'])
    admin.register(User, UserAdmin)
    admin.register(MemberStatus, MemberStatusAdmin)
    admin.register(MemberType, MemberTypeAdmin)
    admin.setup()

    # Limit API access to admins
    api = RestAPI(app, default_auth=AdminAuthentication(
        auth, protected_methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH']))
    api.register(User)
    api.setup()

    # Importing views registers endpoints with Flask
    import dismember.views

    create_builtins(user_datastore)
    app.run(host=app.config['DISMEMBER_HOST'])


def create_builtins(user_datastore):
    """
    Creates the built-in resources (users, etc.) that are defined in the
    config file.
    """

    from dismember.models.user import User

    for builtin_role in app.config['DISMEMBER_BUILTINS']['roles']:
        name = builtin_role['name']
        builtin_role.pop('name')
        user_datastore.find_or_create_role(name, **builtin_role)

    # user_datastore.add_role_to_user('hello', "admin")

    for builtin_user in app.config['DISMEMBER_BUILTINS']['users']:
        if not user_datastore.find_user(username=builtin_user['username']):
            user_datastore.create_user(**builtin_user)
        # if not User.select(User.username == builtin_user['username']).exists():
        #     user = User(**builtin_user)
        #     user.set_password(user.password)
        #     user.enabled = True
        #     user.save()
