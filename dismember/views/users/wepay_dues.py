import datetime

from dismember.models.dues_payment_period import DuesPaymentPeriod
from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, current_user
from dismember.service import app, db
from dismember.dues import dues_service
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from dismember.models.wepay_dues_payment import WePayDuesPayment
from dismember.views.template_helpers import format_currency


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


@app.route('/users/wepay_dues')
@login_required
def users_wepay_dues():
    all_dues_payments = dues_service.get_dues_payments(current_user)

    # Get all the periods covered by all the payments
    paid_periods = []
    for dues_payment in all_dues_payments:
        paid_periods.extend(dues_payment.periods)

    # Take just the most recent ones (at the end)
    recent_paid_periods = sorted(paid_periods, key=lambda p: (p.year, p.month))[-6:]

    if current_user.member_type:
        monthly_dues = format_currency(current_user.member_type.currency, current_user.member_type.monthly_dues)
        past_payable_periods, future_payable_periods = dues_service.generate_payable_periods(current_user)
    else:
        monthly_dues = None
        past_payable_periods = []
        future_payable_periods = []

    return render_template('/users/wepay_dues.html',
                           monthly_dues=monthly_dues,
                           recent_paid_periods=recent_paid_periods,
                           past_payable_periods=past_payable_periods,
                           future_payable_periods=future_payable_periods,
                           utcnow=datetime.datetime.utcnow())


@app.route('/users/wepay_dues_authorize')
@login_required
def users_wepay_dues_authorize():
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
        return 'Missing month parameter(s)', 403

    # Parse the month strings into dues payment periods
    try:
        dues_payment_periods = [DuesPaymentPeriod.from_period_string(period_string) for period_string in months]
    except ValueError as err:
        return 'Error parsing month: %s' % (str(err)), 403

    num_months = len(dues_payment_periods)
    if num_months < 1:
        return 'You have to pay for at least 1 period', 403

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
    checkout.callback_uri = url_for('users_wepay_dues_callback', _external=True)
    checkout.auto_capture = True
    db.session.add(checkout)

    # Create WePayDuesPayments for each dues period
    try:
        wepay_dues_payment = create_dues_payment(checkout, dues_payment_periods)
    except ValueError as err:
        return str(err), 403
    db.session.commit()

    authorize_url = wepay_service.authorize_checkout(checkout, url_for('users_wepay_dues_submit', _external=True))
    db.session.commit()
    return redirect(authorize_url)


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

    submit_url = wepay_service.submit_checkout(url_for('users_wepay_dues_submit', _external=True), state)
    db.session.commit()
    return redirect(submit_url)


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

    checkout, previous_state = wepay_service.refresh_checkout(checkout_id)
    db.session.commit()
    return 'OK', 200