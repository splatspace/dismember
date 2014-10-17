import datetime

from flask import render_template, redirect, url_for, request
from dismember.service import app
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from flask.ext.login import login_required, current_user
from dismember.views.template_helpers import format_currency


@app.route('/users/wepay_dues')
@login_required
def users_wepay_dues():
    recent_payments = DuesPayment.query.filter_by(id=current_user.id).order_by(DuesPayment.created.desc()).limit(
        12).all()
    return render_template('/users/wepay_dues.html',
                           monthly_dues=format_currency(current_user.member_type.currency,
                                                        current_user.member_type.monthly_dues),
                           recent_payments=recent_payments,
                           now=datetime.datetime.utcnow())


@app.route('/users/wepay_dues_authorize')
@login_required
def users_wepay_dues_authorize():
    """Handle the HTTP GET that authorizes a payment and starts the flow through WePay."""
    # user = auth.get_logged_in_user()
    if not current_user.member_type:
        return 'User is not an active member', 403
    if not current_user.member_type.monthly_dues:
        return 'Monthly dues are not configured for the member type %s' % current_user.member_type, 403
    if current_user.member_type.currency != 'USD':
        return 'Monthly dues cannot be paid because the configured currency ' \
               'is "%s" but WePay only supports "USD"' % current_user.member_type.currency, 403

    fee_payer = 'payee'
    if request.args.get('pay_fee', 'false') == 'true':
        fee_payer = 'payer'

    checkout = WePayCheckout()
    checkout.account_id = app.config['WEPAY_ACCOUNT_ID']
    checkout.short_description = '%s dues payment' % (app.config['DISMEMBER_ORG_NAME'])
    checkout.type = 'SERVICE'
    checkout.amount = str(current_user.member_type.monthly_dues)
    checkout.fee_payer = fee_payer
    checkout.callback_uri = url_for('users_wepay_dues_callback', _external=True)
    checkout.auto_capture = True

    return redirect(wepay_service.authorize_checkout(checkout, url_for('users_wepay_dues_submit', _external=True)))


@app.route('/users/wepay_dues_submit')
@login_required
def users_wepay_dues_submit():
    """
    Handle the second part of the WePay payment flow. This is where the user ends up after WePay finishes
    the flow started by users_wepay_dues_authorize.
    """
    state = request.args['state']
    if not state:
        return 'The state parameter is missing', 403

    return redirect(wepay_service.submit_checkout(url_for('users_wepay_dues_submit', _external=True), state))


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