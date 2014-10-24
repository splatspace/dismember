"""
Common view methods for WePay flows.
"""
from dismember.service import db, app
from dismember.wepay import wepay_service
from flask import request, url_for, redirect


@app.route('/wepay/checkout_submit')
def wepay_checkout_submit():
    """
    Handle the second part of the WePay checkout flow. This is where the user ends up after WePay finishes
    the flow started by an authorization.
    """
    state = request.args['state']
    if not state:
        return 'The state parameter is missing', 403

    # Yes, the URL sent to wepay is the URL of this method
    submit_url = wepay_service.submit_checkout(url_for('wepay_checkout_submit', _external=True), state)
    db.session.commit()
    return redirect(submit_url)


@app.route('/wepay/checkout_callback', methods=['POST'])
def wepay_checkout_callback():
    """
    Handle an Instant Payment Notification: an asynchronous POST from WePay about a
    checkout that has changed state (authorized, settled, etc.). Expects the parameters
    that the WePay API docs state will be there.

    This request will be form-encoded (not JSON).
    """
    checkout_id = request.values.get('checkout_id', None)
    if not checkout_id:
        return 'Missing checkout_id', 403

    checkout, previous_state = wepay_service.refresh_checkout(checkout_id)
    db.session.commit()
    return 'OK', 200
