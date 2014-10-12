import urllib
import urllib2
import uuid

from dismember.service import app
from dismember.models.wepay_checkout import WePayCheckout


def to_sparse_dict(o, property_names):
    d = {}
    for name in property_names:
        if hasattr(o, name):
            v = getattr(o, name, None)
            if v is not None:
                d[name] = v
    return d


class WePayApi(object):
    def __init__(self, environment, client_id, client_secret):
        self._environment = environment
        self._client_id = client_id
        self._client_secret = client_secret

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


class WePayService(object):
    def __init__(self, wepay_api):
        self._wepay_api = wepay_api

    def authorize_checkout(self, checkout, submit_uri):
        """
        Authorize a new checkout. This is the first step in the checkout process, in which
        we ask the user to allow us to access his account for the purposes of collecting
        payments.

        This function sets the id and reference_id properties of the checkout to a UUID
        value, overwriting any previously set value. This UUID will be the value of the "state" query
        param when the user returns to the submitUri.

        :param checkout: a WePayCheckout model object
        :param submit_uri: the URI to redirect the user to (with some new query params) after they have authorized
            the checkout at WePay so we can submit it
        :return: the URI the user should visit to authorize the checkout
        """
        assert checkout
        assert checkout.reference_id is None, 'checkout should not have a reference ID yet'
        assert submit_uri

        # Sequential integer IDs are bad to pass in redirects to other sites, where
        # they are visible to the user and the user's agent, because they are guessable.
        # Use an unguessable UUID for this purpose.
        checkout.reference_id = uuid.uuid4()

        # Create it in the database and return the auth URL
        checkout.save()
        return self._wepay_api.get_authorize_url(submit_uri, 'collect_payments', state=checkout.reference_id)

    def submit_checkout(self, submit_uri, authorization_code, checkout_reference_id):
        """
        Submits an authorized checkout to WePay for processing. This is the second step in the
        checkout process.

        :param submit_uri: the exact URI you used as submit_uri for the call to authorize_checkout
        :param authorize_code: the URL query parameter 'code' that WePay included in the redirect back to
            our service after finishing the authorization process initiated by authorize_checkout
        :param checkout_reference_id: the reference ID of the checkout that was previously authorized
        :return: the URI to send the user to to confirm and complete the checkout
        """
        assert submit_uri
        assert authorization_code
        assert checkout_reference_id

        checkout = WePayCheckout.select().where(WePayCheckout.reference_id == checkout_reference_id).first()
        if not checkout:
            raise ValueError('WePayCheckout with reference ID %s not found' % checkout_reference_id)

        # Get an access token for this request for this user
        token = self._wepay_api.get_access_token(submit_uri, authorization_code)

        # Submit the checkout to WePay
        checkout_values = self.to_api(checkout)
        checkout_response = self._wepay_api.call(token, '/checkout/create', checkout_values)

        # Update the DB object with server-side WePay checkout ID
        checkout.checkout_id = checkout_response['checkout_id']
        checkout.save()

        return checkout_response['checkout_uri']


    def _checkout_submit_data(self, checkout):
        """
        Get the checkout submission data, a JSON string that includes the WePayCheckout values appropriate
        for submission.

        :param checkout: a WePayCheckout object being submitted
        :return: a JSON string
        """
        assert checkout
        return to_sparse_dict(checkout, [
            'account_id',
            'short_description',
            'type',
            'amount',
            'currency',
            'long_description',
            'payer_email_message',
            'payee_email_message',
            'reference_id',
            'app_fee',
            'fee_payer',
            'redirect_uri',
            'callback_uri',
            'fallback_uri',
            'auto_capture',
            'require_shipping',
            'shipping_fee',
            'mode',
            'preapproval_id',
            'prefill_info',
            'funding_sources',
            'payment_method_id',
            'payment_method_type'])


wepay_api = WePayApi(app.config['WEPAY_ENVIRONMENT'],
                     app.config['WEPAY_CLIENT_ID'],
                     app.config['WEPAY_CLIENT_SECRET'])
wepay_service = WePayService(wepay_api)
