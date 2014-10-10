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

# Name that will appear in web page titles and e-mails
DISMEMBER_SITE_NAME = 'Dismembership System'

# Resources that will be created each time the service is started, if they do not exist.
DISMEMBER_BUILTINS = {
    'users': [
        {
            # The administrator account.  You can rename it, but don't delete it remove the
            # "Administrator" role mapping.
            'username': 'admin',
            'password': 'admin',
            'full_name': 'Dismember Administrator',
            'email': 'admin@splatspace.org',

            'role_names': ['Administrator']
        }
    ],
    'roles': [
        {
            # The full administrator role.  Don't rename or delete this one.
            'name': 'Administrator',
            'description': 'Full Administrator',
        }
    ],
}
