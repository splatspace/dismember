import datetime

from dismember.currency import format_currency
from dismember.models.dues_payment_period import DuesPaymentPeriod
from dismember.user import user_bp
from flask import render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user
from dismember.service import app, db
from dismember.dues import dues_service
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from dismember.models.wepay_dues_payment import WePayDuesPayment



def create_dues_payment(checkout, dues_payment_periods):
    """
    Create a WePayDuesPayment for the specified periods.

    :param checkout: the WePayCheckout to link the payment to
    :param dues_payment_periods: iterable of DuesPaymentPeriods
    :return: the created WePayDuesPayment
    """
    pmt = WePayDuesPayment()
    pmt.user_id = current_user.id
    pmt.wepay_checkout = checkout
    db.session.add(pmt)

    for period in dues_payment_periods:
        # Check for non-void payments of any type that conflict with the year and month
        existing_payment = DuesPayment.query \
            .filter_by(user_id=current_user.id, void=False) \
            .join(DuesPayment.periods) \
            .filter_by(year=period.year, month=period.month) \
            .first()

        # Ignore payments in "exception" (we'll assume a manual approval was given to re-pay for that period).
        if existing_payment and existing_payment.exception is None:
            raise ValueError(
                'You have already made a dues payment for the month of {:04d}-{:02d}.  '
                'Adjust the start month and number of months so this month is not included.'.format(
                    period.year, period.month))

        period.dues_payment_id = pmt.id
        db.session.add(period)

    return pmt


@user_bp.route('/wepay/dues')
@login_required
def wepay_dues():
    all_dues_payments = dues_service.get_dues_payments(current_user)

    # Get all the periods covered by all the payments
    paid_periods = []
    for dues_payment in all_dues_payments:
        paid_periods.extend(dues_payment.periods)

    # Take just the most recent ones (at the end)
    recent_paid_periods = sorted(paid_periods, key=lambda p: (p.year, p.month))[-6:]

    if current_user.member_type:
        past_payable_periods, future_payable_periods = dues_service.generate_payable_periods(current_user)
    else:
        past_payable_periods = []
        future_payable_periods = []

    return render_template('/user/wepay_dues.html',
                           recent_paid_periods=recent_paid_periods,
                           past_payable_periods=past_payable_periods,
                           future_payable_periods=future_payable_periods,
                           utcnow=datetime.datetime.utcnow())


@user_bp.route('/wepay/dues_authorize')
@login_required
def wepay_dues_authorize():
    """Handle the HTTP GET that authorizes a payment and starts the flow through WePay."""
    if not current_user.member_type:
        return 'User is not an active member', 403
    if not current_user.member_type.monthly_dues:
        return 'Monthly dues are not configured for the member type %s' % current_user.member_type, 403
    if current_user.member_type.currency != 'USD':
        return 'Monthly dues cannot be paid because the configured currency ' \
               'is "%s" but WePay only supports "USD"' % current_user.member_type.currency, 403

    months = request.args.getlist('month', None)
    if not months:
        flash('You must select at least one period.', 'error')
        return redirect(url_for('.wepay_dues'))

    # Parse the month strings into dues payment periods
    try:
        dues_payment_periods = [DuesPaymentPeriod.from_period_string(period_string) for period_string in months]
    except ValueError as err:
        flash('Error parsing month: %s' % (str(err)), 'error')
        return redirect(url_for('.wepay_dues'))

    num_months = len(dues_payment_periods)
    if num_months < 1:
        flash('You must select at least one period.', 'error')
        return redirect(url_for('.wepay_dues'))

    fee_payer = 'payee'
    if 'pay_fee' in request.args:
        fee_payer = 'payer'

    amount = current_user.member_type.monthly_dues * num_months

    checkout = WePayCheckout()
    checkout.account_id = app.config['WEPAY_ACCOUNT_ID']
    checkout.short_description = '%s dues (%d months)' % (app.config['DISMEMBER_ORG_NAME'], num_months)
    checkout.type = 'SERVICE'
    checkout.amount = str(amount)
    checkout.fee_payer = fee_payer
    checkout.callback_uri = url_for('.wepay_checkout_callback', _external=True)
    checkout.auto_capture = True
    db.session.add(checkout)

    # Create WePayDuesPayments for each dues period
    try:
        wepay_dues_payment = create_dues_payment(checkout, dues_payment_periods)
    except ValueError as err:
        return str(err), 403
    db.session.commit()

    authorize_url = wepay_service.authorize_checkout(checkout, url_for('.wepay_checkout_submit', _external=True))
    db.session.commit()
    return redirect(authorize_url)
