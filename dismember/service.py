from flask import Flask

from dismember.reverse_proxied import ReverseProxied
from flask.ext.admin import Admin
from flask.ext.security import Security
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
    security = Security(app, user_datastore)

    # Flask-Admin
    admin = Admin(app, name=app.config['DISMEMBER_SITE_NAME'])

    # Flask-Admin
    # from dismember.models.currency import Currency, CurrencyAdmin
    # from dismember.models.dues_payment import DuesPayment, DuesPaymentAdmin
    # from dismember.models.member_type import MemberType, MemberTypeAdmin
    # from dismember.models.user import User, UserAdmin
    # from dismember.models.wepay_checkout import WePayCheckout, WePayCheckoutAdmin
    # from dismember.models.wepay_dues_payment import WePayDuesPayment, WePayDuesPaymentAdmin
    #
    # auth = Auth(app, db, user_model=dismember.models.user.User)
    # admin = Admin(app, auth, branding=app.config['DISMEMBER_SITE_NAME'])
    # admin.register(Currency, CurrencyAdmin)
    # admin.register(DuesPayment, DuesPaymentAdmin)
    # admin.register(MemberType, MemberTypeAdmin)
    # admin.register(User, UserAdmin)
    # admin.register(WePayCheckout, WePayCheckoutAdmin)
    # admin.register(WePayDuesPayment, WePayDuesPaymentAdmin)
    # admin.setup()

    # Limit API access to admins
    # api = RestAPI(app, default_auth=AdminAuthentication(
    # auth, protected_methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH']))
    # api.register(User)
    # api.setup()

    # Importing views registers endpoints with Flask
    import dismember.views

    create_builtins(db, user_datastore)
    app.run(host=app.config['DISMEMBER_HOST'])


def create_builtins(db, user_datastore):
    """
    Creates the built-in resources (users, etc.) that are defined in the
    config file.
    """

    # Use an application context so we can use flask utils that require one
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
            for role_name in builtin['roles']:
                user_datastore.add_role_to_user(user, role_name)

        db.session.commit()