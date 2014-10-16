import datetime

from flask import render_template, redirect, url_for, request
from dismember.service import app, auth
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout


@app.route('/users/wepay_dues')
@auth.login_required
def users_wepay_dues():
    user = auth.get_logged_in_user()
    if user:
        last_dues_payment = DuesPayment \
            .select() \
            .where(DuesPayment.user == user.id) \
            .order_by(DuesPayment.created.desc()).first()

    return render_template('/users/wepay_dues.html', last_dues_payment=last_dues_payment or None,
                           now=datetime.datetime.utcnow())


@app.route('/users/wepay_dues_authorize')
@auth.login_required
def users_wepay_dues_authorize():
    """Handle the HTTP GET that authorizes a payment and starts the flow through WePay."""
    user = auth.get_logged_in_user()
    if not user:
        return 'No current user', 403
    if not user.member_type:
        return 'User is not an active member', 403
    if not user.member_type.monthly_dues:
        return 'Monthly dues are not configured for the member type %s' % user.member_type, 403
    if user.member_type.currency.name != 'USD':
        return 'Monthly dues cannot be paid because the configured currency ' \
               'is "%s" but WePay only supports "USD"' % user.member_type.currency.name, 403

    fee_payer = 'payee'
    if request.args.get('pay_fee', 'false') == 'true':
        fee_payer = 'payer'

    checkout = WePayCheckout()
    checkout.account_id = app.config['WEPAY_ACCOUNT_ID']
    checkout.short_description = '%s dues payment' % (app.config['DISMEMBER_ORG_NAME'])
    checkout.type = 'SERVICE'
    checkout.amount = str(user.member_type.monthly_dues)
    checkout.fee_payer = fee_payer
    checkout.callback_uri = url_for('users_wepay_dues_callback', _external=True)
    checkout.auto_capture = True

    return redirect(wepay_service.authorize_checkout(checkout, url_for('users_wepay_dues_submit', _external=True)))


@app.route('/users/wepay_dues_submit')
@auth.login_required
def users_wepay_dues_submit():
    """
    Handle the second part of the WePay payment flow. This is where the user ends up after WePay finishes
    the flow started by users_wepay_dues_authorize.
    """
    checkout_reference_id = request.args['state']
    if not checkout_reference_id:
        return 'The state does not contain a checkout reference ID', 403

    return redirect(
        wepay_service.submit_checkout(url_for('users_wepay_dues_submit', _external=True), checkout_reference_id))


@app.route('/users/wepay_dues_callback', methods=['POST'])
def users_wepay_dues_callback():
    """
    Handle an Instant Payment Notification: an asynchronous POST from WePay about a
    checkout that has changed state (authorized, settled, etc.). Expects the parameters
    that the WePay API docs state will be there.

    This request will be form-encoded (not JSON).
    """
    checkout_id = request.values.get('checkout_id', None)
    if not checkout_id:
        return 'Missing checkout_id', 403

    wepay_service.refresh_checkout(checkout_id)
    return 'OK', 200