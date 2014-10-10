import datetime

config = {
    # Flask-peewee "DATABASE" config dictionary.
    'db': {
        # Required
        'engine': 'peewee.PostgresqlDatabase',
        # Required
        'name': 'dismember',

        # Any driver keyword arguments can be included here (username, password, etc.)
    },

    'flask': {
        # The host or interface to bind to
        'bind': '0.0.0.0',

        # Enables the Flask debugger (never enable this in production)
        'debug': True,

        # Secret key for signing session cookies
        'session_secret_key': '9fb732e3fb1b54ff79a22b8b7efc8cc0b57d7a653e690339710a94acb87ce173',

        # Salt for PBKDF2 function
        'password_salt': '266f06d86484d7eccdadbeee6d6652e44d9eb1be75c8e285d5263539b6cfcf40',

        # How long the "remember me" cookies stay valid
        'remember_me_cookie_duration': datetime.timedelta(days=45)
    },

    # Resources that will be created each time the service is started, if they do not exist.
    'builtins': {
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
    },

    # Site-wide settings
    'site': {
        'name': 'Splat Space Membership',
    },
}
