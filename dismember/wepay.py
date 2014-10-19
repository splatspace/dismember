import json
import uuid

from dismember import wepay_api
from dismember.models.wepay_checkout import WePayCheckout


class WePayService(object):
    """
    Manages WePay information locally and remotely through the WePay web service (using
    WePayApi).
    """

    def __init__(self, api):
        self._api = api

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

        # Pack up some state information that we can use in the submit step
        state = checkout.reference_id

        return self._api.get_authorize_url(submit_uri, 'collect_payments', state)

    def submit_checkout(self, submit_uri, state):
        """
        Submits an authorized checkout to WePay for processing. This is the second step in the
        checkout process.

        :param submit_uri: the exact URI you used as submit_uri for the call to authorize_checkout
        :param state: the "state" query argument value that was supplied when WePay redirected the user back after the
            authorization
        :return: the URI to send the user to to confirm and complete the checkout
        """
        assert submit_uri
        assert state

        # Unpack the state from the last authorize
        checkout_reference_id = state

        checkout = WePayCheckout.query.filter_by(reference_id=checkout_reference_id).first()
        if checkout is None:
            raise ValueError('WePayCheckout with reference ID %s not found' % checkout_reference_id)

        # Submit only the values that are valid for 'create' to WePay.  Use the default access token
        # since we're only accessing our account.
        checkout_response = json.loads(
            self._api.call('/checkout/create', request_data=checkout.to_create_dict()))

        # Update the local model (we'll receive an IPN callback soon with even more info)
        checkout.update_from_dict(checkout_response)
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
        checkout_response = json.loads(self._api.call('/checkout', request_data=dict(checkout_id=checkout_id)))

        if not checkout_response:
            raise ValueError('No checkout with ID %s was found' % checkout_id)

        # We generate the reference ID, and they're unique, so they are the best key in this situation
        checkout = WePayCheckout.query.filter_by(reference_id=checkout_response['reference_id']).first()
        if checkout is None:
            raise ValueError('WePayCheckout with reference ID %s not found' % checkout_response['reference_id'])

        previous_state = checkout.state
        checkout.update_from_dict(checkout_response)
        return checkout, previous_state


wepay_service = WePayService(wepay_api.wepay_api)
