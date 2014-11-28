# Configuration defaults for dismember.  During development, don't edit this file;
# instead create ../instance/config.py and override values there.
import datetime

# ######################################################################
# Flask
#
# See http://flask.pocoo.org/docs/0.10/api/
# Default values at http://flask.pocoo.org/docs/0.10/api/#flask.Flask.default_config

# Enables debug information in the logs and in error pages (never enable this in
# production)
DEBUG = False

# Every installation should use a different value for the secret key.
# Get a good value with:
#
# head -c 100 /dev/urandom | sha256sum | cut -f 1 -d " "
#
SECRET_KEY = 'f99b15e00bc813d5a027e902d177c56fcba1a5027bff1b0a54b8c7338dbead29'

# ######################################################################
# Flask-SQLAlchemy
#

SQLALCHEMY_DATABASE_URI = 'postgresql:///dismember'
SQLALCHEMY_ECHO = False

# ######################################################################
# Flask-Security
#

SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'

# Every installation should use a different value for the salt.
# Get a good value with:
#
# head -c 100 /dev/urandom | sha256sum | cut -f 1 -d " "
#
SECURITY_PASSWORD_SALT = '3307b48c305151a73a7d4a0100b670adda9858d8f09057591089c93dfdbc0e90'

# ######################################################################
# Flask-Login
#

REMEMBER_COOKIE_DURATION = datetime.timedelta(days=45)

# ######################################################################
# Flask-Email
#

MAIL_SERVER = 'localhost'
MAIL_PORT = 25
# MAIL_USE_SSL = True
# MAIL_USERNAME = 'username'
# MAIL_PASSWORD = 'password'


# ######################################################################
# Dismember
#

# Host or IP to bind to
DISMEMBER_HOST = '0.0.0.0'

# TCP port to listen on
DISMEMBER_PORT = 5005

# The name of the organization that will appear in web page titles and e-mails
DISMEMBER_ORG_NAME = 'Splat Space'

# Name that will appear in web page titles and e-mails
DISMEMBER_SITE_NAME = 'Dismembership System'

# Resources that will be created each time the service is started, if they do not exist.
DISMEMBER_BUILTINS = {
    'roles': [
        {
            # The administrator role.  Don't rename or delete this role.
            'name': 'admin',
            'description': 'Organization administrator with full access'
        },
        {
            # The board member role.  Don't rename or delete this role.
            'name': 'board',
            'description': 'A member of the board of directors'
        }
    ],
    'users': [
        {
            # The administrator account.  Change the email and password before running
            # the software for the first time.  You can change the full name at any time.
            #
            # Don't delete this user or remove the "admin" role (that would be silly).
            'email': 'admin@example.org',
            'password': 'admin',
            'full_name': 'Site Administrator',
            'roles': ['admin', 'board']
        }
    ]
}

# 'prod' or 'stage'
WEPAY_ENVIRONMENT = 'stage'

# Your WePay account ID.  You can find this in the API Keys web page at WePay.
WEPAY_ACCOUNT_ID = '12345'

# The WePay access token for your account.  You can find this in the API Keys web page at WePay.
WEPAY_ACCESS_TOKEN = 'STAGE_abc123def456'

# Your WePay application's client ID.  You can find this in the API Keys web page at WePay.
WEPAY_CLIENT_ID = '67890'

# Your WePay application's client secret.  You can find this in the API Keys web page at WePay.
WEPAY_CLIENT_SECRET = '123abc456xyz'

