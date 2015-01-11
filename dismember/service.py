from flask import Flask

from dismember.reverse_proxied import ReverseProxied
# from flask.ext.admin import Admin
# from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.bootstrap import Bootstrap
from flask.ext.security import Security
from flask.ext.security.confirmable import confirm_user
from flask.ext.security.datastore import SQLAlchemyUserDatastore

# Don't import any modules that use DB models up here, because they need to
# import and use the "db" object from this module (which would not be initialized
# yet).  Instead, import them as requred after db has been initialized.  This
# file is the only file that requires this special treatment.  Other files can
# import and use models freely.
from flask.ext.mail import Mail
from flask.ext.security.utils import encrypt_password
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_object('dismember.config')
# Read the local "./instance/config.py" if it exists
app.config.from_pyfile('config.py', silent=True)

# Initialized by run
db = None
mail = None
security = None
admin = None


def run():
    global app, db, mail, security, admin

    # Flask-SQLAlchemy
    db = SQLAlchemy(app)

    # Import all models (this must be done after db is assigned)
    import dismember.models

    db.create_all()

    # Flask-Mail
    mail = Mail(app)
    app.mail = mail

    # Flask-Security Core
    user_datastore = SQLAlchemyUserDatastore(db, dismember.models.user.User, dismember.models.role.Role)
    app.config['SECURITY_URL_PREFIX'] = '/security'
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_TRACKABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True
    security = Security(app, user_datastore)

    # Import the CRUD blueprint so views can use it
    from dismember.crud import crud_bp

    app.register_blueprint(crud_bp)

    # Import normal views so they can register endpoints with Flask
    import dismember.views

    # Flask-Bootstrap
    bootstrap = Bootstrap(app)

    from dismember.admin import admin_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')

    create_builtins(db, user_datastore)
    app.run(host=app.config['DISMEMBER_HOST'], port=app.config['DISMEMBER_PORT'])


def create_builtins(the_db, user_datastore):
    """
    Creates the built-in resources (users, etc.) that are defined in the
    config file.
    """

    # Some flask utils like encrypt_password require an application context
    with app.app_context():
        # Roles
        for builtin in app.config['DISMEMBER_BUILTINS']['roles']:
            user_datastore.find_or_create_role(**builtin)

        # Users
        for builtin in app.config['DISMEMBER_BUILTINS']['users']:
            user = user_datastore.find_user(email=builtin['email'])
            if not user:
                # Hash the password
                builtin['password'] = encrypt_password(builtin.pop('password', ''))
                user = user_datastore.create_user(**builtin)
            confirm_user(user)
            for role_name in builtin['roles']:
                user_datastore.add_role_to_user(user, role_name)

        the_db.session.commit()