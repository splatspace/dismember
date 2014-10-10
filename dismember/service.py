from flask import Flask
from flask.ext.peewee.admin import Admin
from flask.ext.peewee.auth import Auth
from flask.ext.peewee.rest import RestAPI, AdminAuthentication
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

    # Flask-Peewee
    from dismember.models.user import User, UserAdmin
    from dismember.models.member_status import MemberStatus, MemberStatusAdmin
    from dismember.models.member_type import MemberType, MemberTypeAdmin

    auth = Auth(app, db, user_model=dismember.models.user.User)
    admin = Admin(app, auth, branding=app.config['DISMEMBER_SITE_NAME'])
    admin.register(User, UserAdmin)
    admin.register(MemberStatus, MemberStatusAdmin)
    admin.register(MemberType, MemberTypeAdmin)
    admin.setup()

    # Limit API access to admins
    api = RestAPI(app, default_auth=AdminAuthentication(
        auth, protected_methods=['HEAD', 'GET', 'POST', 'PUT', 'DELETE']))
    api.register(User)
    api.setup()

    # Importing views registers endpoints with Flask
    import dismember.views

    create_builtins()
    app.run(host=app.config['DISMEMBER_HOST'])


def create_builtins():
    """
    Creates the built-in resources (users, etc.) that are defined in the
    config file.
    """

    from dismember.models.user import User

    # Create builtin users
    for builtin_user in app.config['DISMEMBER_BUILTINS']['users']:
        if not User.select(User.username == builtin_user['username']).exists():
            user = User(**builtin_user)
            user.set_password(user.password)
            user.enabled = True
            user.save()
