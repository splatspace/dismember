import urllib
import urllib2


class WePayApi(object):
    def __init__(self, environment, client_id, client_secret):
        self._environment = environment
        self._client_id = client_id
        self._client_secret = client_secret

    def get_authorize_url(self, redirect_uri, scope, state):
        """
         Get a URL from WePay that you can send to the end-user so they can authorize your
         account to access their account for the purpose you specify.

         When the user finally reaches your redirectUri, the query params include a 'code', which
         you will need to save for calls to getAccessToken. The query params also include 'state',
         if you supplied any.

        :param redirect_uri: the URI you want the user to come back to after completing the web authorization
        :param scope: the WePay authorization scopes you want (see WePay API documentation for valid strings)
        :param state: your state data; is carried through the auth flow and returns as a query param when the user reaches your redirectUri
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

    def get_access_token(self, redirect_uri, code, callback_uri):
        """
        Get an access token for making API requests. You must first call get_authorize_url to
        obtain 'code'.

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
        return urllib2.open(url).read()

    def call(self, access_token, method, request_data):
        """
        Call a WePay API method.

        :param access_token: an access token you got from get_access_token
        :param method: the name of the method (like '/checkout/create')
        :param request_data: the parameters for the call
        :return: the response data from the API
        """
        assert access_token
        assert method
        if self._environment == 'prod':
            base_url = 'https://wepayapi.com/v2'
        elif self._environment == 'stage':
            base_url = 'https://stage.wepayapi.com/v2'

        url = base_url + method
        request = urllib2.Request(url, request_data)
        request.add_header('Authorization', 'Bearer ' + access_token)
        return urllib2.urlopen(request).read()