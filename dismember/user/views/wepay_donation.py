import datetime
from decimal import InvalidOperation
import decimal

from dismember.currency import format_currency
from dismember.donations import donation_service
from dismember.models.wepay_donation_payment import WePayDonationPayment
from dismember.user import user_bp
from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, current_user
from dismember.service import app, db
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from flask.ext.security import AnonymousUser


def create_donation_payment(checkout):
    """
    Create a WePayDonationPayment for the specified periods.

    :param checkout: the WePayCheckout to link the payment to
    :return: the created WePayDonationPayment
    """
    pmt = WePayDonationPayment()
    pmt.user_id = current_user.id
    pmt.wepay_checkout = checkout
    db.session.add(pmt)
    return pmt


@user_bp.route('/wepay/donation')
@login_required
def wepay_donation():
    all_donation_payments = donation_service.get_donation_payments(current_user)

    # Take just the most recent ones (at the end)
    recent_donation_payments = sorted(all_donation_payments, key=lambda p: p.created_at)[-6:]

    if current_user.member_type:
        monthly_dues = format_currency(current_user.member_type.currency, current_user.member_type.monthly_dues)
    else:
        monthly_dues = None

    return render_template('/user/wepay_donation.html',
                           monthly_dues=monthly_dues,
                           recent_donation_payments=recent_donation_payments,
                           utcnow=datetime.datetime.utcnow())


@user_bp.route('/wepay/donation_authorize')
@login_required
def wepay_donation_authorize():
    """Handle the HTTP GET that authorizes a payment and starts the flow through WePay."""

    if current_user is AnonymousUser:
        user = None
    else:
        user = current_user

    fee_payer = 'payee'
    if 'pay_fee' in request.args:
        fee_payer = 'payer'

    if 'amount' not in request.args:
        return 'Missing amount in request args', 403
    amount = request.args['amount']

    # Parse with decimal as validation
    try:
        decimal_amount = decimal.Decimal(amount)
    except InvalidOperation:
        return 'Invalid amount', 403

    # Don't allow small or negative amounts
    if decimal_amount < 1:
        return 'Amount must be at least 1', 403

    checkout = WePayCheckout()
    checkout.account_id = app.config['WEPAY_ACCOUNT_ID']
    checkout.short_description = '%s donation' % (app.config['DISMEMBER_ORG_NAME'])
    checkout.type = 'DONATION'
    checkout.amount = amount
    checkout.fee_payer = fee_payer
    checkout.callback_uri = url_for('.wepay_checkout_callback', _external=True)
    checkout.auto_capture = True
    db.session.add(checkout)

    create_donation_payment(checkout)
    db.session.commit()

    authorize_url = wepay_service.authorize_checkout(checkout, url_for('.wepay_checkout_submit', _external=True))
    db.session.commit()
    return redirect(authorize_url)

