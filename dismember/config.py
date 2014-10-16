# Configuration defaults for dismember.  During development, don't edit this file;
# instead create ../instance/config.py and override values there.

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
# head -c 1000 /dev/urandom | sha256sum | cut -f 1 -d " "
#
SECRET_KEY = 'f99b15e00bc813d5a027e902d177c56fcba1a5027bff1b0a54b8c7338dbead29'

# Sets the host name to respond to requests at, and for use in absolute URLs that
# reference this server.  If you're getting 404s for every page, make sure this setting
# matches the host:port that your user agent (browser) is requesting from.
#
# This does set the interface or port that Flask binds to.  It only defines
# the host and port part of URLs that it will respond to.
SERVER_NAME = 'localhost:5000'

# Sets the scheme to use in absolute URLs that reference this server.
#
# This does not set the protocol that Flask speaks.  It only defines the scheme
# to use in generated URLs.
PREFERRED_URL_SCHEME = 'http'

# ######################################################################
# Flask-Peewee
#
# As of 2014-10-10 "DATABASE" is the only config property Flask-Peewee
# uses.

# http://flask-peewee.readthedocs.org/en/latest/database.html
DATABASE = {
    'engine': 'peewee.PostgresqlDatabase',
    'name': 'dismember'
    # Any driver keyword arguments (username, password, etc.) as additional properties
}

# ######################################################################
# Dismember
#

# Host or IP to bind to
DISMEMBER_HOST = '0.0.0.0'

# The name of the organization that will appear in web page titles and e-mails
DISMEMBER_ORG_NAME = 'Splat Space'

# Name that will appear in web page titles and e-mails
DISMEMBER_SITE_NAME = 'Dismembership System'

# Resources that will be created each time the service is started, if they do not exist.
DISMEMBER_BUILTINS = {
    'users': [
        {
            # The administrator account.  You can rename it, but don't delete it or
            # set the "admin" property to False (that would be very silly).
            'username': 'admin',
            'password': 'admin',
            'full_name': 'Dismember Administrator',
            'email': 'admin@example.org',
            'admin': True
        }
    ],
    'payment_methods': [
        {
            'name': 'Cash',
            'description': 'A payment made with cash',
        },
        {
            'name': 'Check',
            'description': 'A payment made with a paper check',
        },
        {
            'name': 'WePay',
            'description': 'A payment made through the WebPay API',
        }
    ],
    # Currency names must be ISO 4217 codes
    'currencies': [
        {
            'name': 'USD',
            'symbol': '$'
        }
    ]
}

# 'prod' or 'stage'
WEPAY_ENVIRONMENT = 'stage'

# Your WePay account ID
WEPAY_ACCOUNT_ID = '12345'

# Your WePay access token.  Used with API methods that don't require a dynamic per-user token.
WEPAY_DEFAULT_ACCESS_TOKEN = 'STAGE_abc123def456'

# Your WePay application's client ID
WEPAY_CLIENT_ID = '67890'

# Your WePay application's client secret
WEPAY_CLIENT_SECRET = '123abc456xyz'

