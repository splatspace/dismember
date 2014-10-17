import urllib
import urllib2
import json
import uuid

from dismember.service import app, db
from dismember.models.wepay_checkout import WePayCheckout


class WePayApi(object):
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
        checkout.reference_id = str(uuid.uuid4())

        # Add it to the database and return the auth URL
        db.session.add(checkout)
        db.session.commit()
        return self._wepay_api.get_authorize_url(submit_uri, 'collect_payments', state=checkout.reference_id)

    def submit_checkout(self, submit_uri, checkout_reference_id):
        """
        Submits an authorized checkout to WePay for processing. This is the second step in the
        checkout process.

        :param submit_uri: the exact URI you used as submit_uri for the call to authorize_checkout
        :param checkout_reference_id: the reference ID of the checkout that was previously authorized
        :return: the URI to send the user to to confirm and complete the checkout
        """
        assert submit_uri
        assert checkout_reference_id

        checkout = WePayCheckout.query.filter_by(reference_id=checkout_reference_id).first()
        if checkout is None:
            raise ValueError('WePayCheckout with reference ID %s not found' % checkout_reference_id)

        # Submit only the values that are valid for 'create' to WePay.  Use the default access token
        # since we're only accessing our account.
        checkout_response = json.loads(
            self._wepay_api.call('/checkout/create', request_data=checkout.to_create_dict()))

        # Update the DB object with server-side WePay checkout ID
        checkout.update_from_dict(checkout_response)
        db.session.commit()

        return checkout_response['checkout_uri']

    def refresh_checkout(self, checkout_id):
        """
        Refresh local information about a checkout from the WePay API.  This method is primary
        for callback handlers.

        :param checkout_id: the ID WePay assigned to the checkout after it was created
        :return: the refreshed WePayCheckout object, the "state" property of the object before the refresh
        """
        assert checkout_id

        # Use the default access token.
        checkout_response = json.loads(self._wepay_api.call('/checkout', request_data=dict(checkout_id=checkout_id)))

        if not checkout_response:
            raise ValueError('No checkout with ID %s was found' % checkout_id)

        # We generate the reference ID, and they're unique, so they are the best key in this situation
        checkout = WePayCheckout.query.filter_by(reference_id=checkout_response['reference_id']).first()
        if checkout is None:
            raise ValueError('WePayCheckout with reference ID %s not found' % checkout_response['reference_id'])

        previous_state = checkout.state
        checkout.update_from_dict(checkout_response)
        db.session.commit()
        return checkout, previous_state


wepay_api = WePayApi(app.config['WEPAY_ENVIRONMENT'],
                     app.config['WEPAY_CLIENT_ID'],
                     app.config['WEPAY_CLIENT_SECRET'],
                     app.config['WEPAY_ACCESS_TOKEN'])
wepay_service = WePayService(wepay_api)
