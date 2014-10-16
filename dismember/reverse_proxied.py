class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    Adapted from http://flask.pocoo.org/snippets/35/.  X-Path-Prefix
    used instead of X-Script-Name because it's a more accurate description
    of what's being specified.

    In nginx:
    location /myprefix {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Path-Prefix /myprefix;
        }


    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path_prefix = environ.get('HTTP_X_PATH_PREFIX', '')
        if path_prefix:
            environ['SCRIPT_NAME'] = path_prefix
            path_info = environ['PATH_INFO']
            if path_info.startswith(path_prefix):
                environ['PATH_INFO'] = path_info[len(path_prefix):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)
