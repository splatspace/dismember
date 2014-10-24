import datetime
from dismember.donations import donation_service

from dismember.models.dues_payment_period import DuesPaymentPeriod
from dismember.models.wepay_donation_payment import WePayDonationPayment
from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, current_user
from dismember.service import app, db
from dismember.dues import dues_service
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from dismember.views.template_helpers import format_currency
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


@app.route('/users/wepay_donation')
@login_required
def users_wepay_donation():
    all_donation_payments = donation_service.get_donation_payments(current_user)

    # Take just the most recent ones (at the end)
    recent_donation_payments = sorted(all_donation_payments, key=lambda p: p.created)[-6:]

    return render_template('/users/wepay_donation.html',
                           recent_donation_payments=recent_donation_payments,
                           utcnow=datetime.datetime.utcnow())


@app.route('/users/wepay_donation_authorize')
@login_required
def users_wepay_donation_authorize():
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

    checkout = WePayCheckout()
    checkout.account_id = app.config['WEPAY_ACCOUNT_ID']
    checkout.short_description = '%s donation' % (app.config['DISMEMBER_ORG_NAME'])
    checkout.type = 'DONATION'
    checkout.amount = amount
    checkout.fee_payer = fee_payer
    checkout.callback_uri = url_for('wepay_checkout_callback', _external=True)
    checkout.auto_capture = True
    db.session.add(checkout)
    db.session.commit()

    authorize_url = wepay_service.authorize_checkout(checkout, url_for('wepay_checkout_submit', _external=True))
    db.session.commit()
    return redirect(authorize_url)

