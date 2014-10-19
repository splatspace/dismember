import urllib
import urllib2
import json

from dismember.service import app


class WePayApi(object):
    """
    Interfaces with WePay through the web service API.
    """

    def __init__(self, environment, client_id, client_secret, default_access_token):
        self._environment = environment
        self._client_id = client_id
        self._client_secret = client_secret
        self._default_access_token = default_access_token

    def get_authorize_url(self, redirect_uri, scope, state=None):
        """
         Get a URL from WePay that you can send to the end-user so they can authorize your
         account to access their account for the purpose you specify.

         When the user finally reaches your redirectUri, the query params include a 'code', which
         you will need to save for calls to getAccessToken. The query params also include 'state',
         if you supplied any.

        :param redirect_uri: the URI you want the user to come back to after completing the web authorization
        :param scope: the WePay authorization scopes you want (see WePay API documentation for valid strings)
        :param state: your state data; is carried through the auth flow and returns as a query param when the
            user reaches your redirectUri
        :return: the URL to send to the user so they can authorize your access to their account
        """
        assert redirect_uri
        assert scope
        if self._environment == 'prod':
            base_url = 'https://www.wepay.com/v2/oauth2/authorize'
        elif self._environment == 'stage':
            base_url = 'https://stage.wepay.com/v2/oauth2/authorize'

        params = dict(
            client_id=self._client_id,
            redirect_uri=redirect_uri,
            scope=scope)

        if state:
            params['state'] = state

        return '%s?%s' % (base_url, urllib.urlencode(params))

    def get_access_token(self, redirect_uri, code, callback_uri=None):
        """
        Get an access token for making API requests on behalf of a user who has authorized you
        to do so (through the flow started by get_authorize_url).

        :param redirect_uri: the URI that you used for get_authorize_url
        :param code: the code you got back as a query param from get_authorize_url
        :param callback_uri: a URI to receive callbacks
        :return: the access token string
        """
        assert redirect_uri
        assert code
        if self._environment == 'prod':
            base_url = 'https://wepayapi.com/v2/oauth2/token'
        elif self._environment == 'stage':
            base_url = 'https://stage.wepayapi.com/v2/oauth2/token'

        params = dict(
            client_id=self._client_id,
            redirect_uri=redirect_uri,
            client_secret=self._client_secret,
            code=code)

        # Optional
        if callback_uri:
            params['callback_uri'] = callback_uri

        url = '%s?%s' % (base_url, urllib.urlencode(params))
        return urllib2.urlopen(url).read()

    def call(self, method, request_data={}, access_token=None):
        """
        Call a WePay API method.

        :param method: the name of the method (like '/checkout/create')
        :param request_data dict: the call request parameters
        :param access_token: an access token you got from get_access_token or None to use the default token
        :return: the response data from the API
        """
        assert method

        if access_token is None:
            access_token = self._default_access_token

        if self._environment == 'prod':
            base_url = 'https://wepayapi.com/v2'
        elif self._environment == 'stage':
            base_url = 'https://stage.wepayapi.com/v2'

        url = base_url + method
        request = urllib2.Request(url, data=json.dumps(request_data))
        request.add_header('Authorization', 'Bearer ' + access_token)
        request.add_header('Content-Type', 'application/json')
        return urllib2.urlopen(request).read()

# A default instance of WePayApi configured for the Dismember service
wepay_api = WePayApi(app.config['WEPAY_ENVIRONMENT'],
                     app.config['WEPAY_CLIENT_ID'],
                     app.config['WEPAY_CLIENT_SECRET'],
                     app.config['WEPAY_ACCESS_TOKEN'])
