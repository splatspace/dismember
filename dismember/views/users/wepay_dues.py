import datetime

from dateutil import relativedelta
from dismember.models.dues_payment_period import DuesPaymentPeriod
from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, current_user
from dismember.service import app, db
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from dismember.models.wepay_dues_payment import WePayDuesPayment
from dismember.views.template_helpers import format_currency


def create_dues_payment(checkout, month_tuples):
    """
    Create a WePayDuesPayment with periods for the specified months.

    :param checkout: the WePayCheckout to link the payment to
    :param month_tuples: iterable of integer (year, month) tuples
    :return: the created WePayDuesPayment
    """
    pmt = WePayDuesPayment()
    pmt.user_id = current_user.id
    pmt.wepay_checkout = checkout
    db.session.add(pmt)

    for (year, month) in month_tuples:
        # Check for non-void payments of any type that conflict with the year and month
        existing_payment = DuesPayment.query \
            .filter_by(user_id=current_user.id, void=False) \
            .join(DuesPayment.periods) \
            .filter_by(year=year, month=month) \
            .first()

        # Ignore payments in "exception" (we'll assume a manual approval was given to re-pay for that period).
        if existing_payment and existing_payment.exception is None:
            raise ValueError(
                'You have already made a dues payment for the month of {:04d}-{:02d}.  '
                'Adjust the start month and number of months so this month is not included.'.format(
                    year, month))

        period = DuesPaymentPeriod()
        period.dues_payment_id = pmt.id
        period.year = year
        period.month = month
        db.session.add(period)

    return pmt


def get_successful_dues_payments():
    # Find all of this user's non-void dues payments
    dues_payments = DuesPayment.query \
        .filter_by(user_id=current_user.id, void=False) \
        .all()

    # Retain only those without exceptions
    dues_payments = filter(lambda p: p.exception is None, dues_payments)

    # Extract (year, month) tuples for easy searching
    year_month_tuples = set()
    for pmt in dues_payments:
        for period in pmt.periods:
            year_month_tuples.add((period.year, period.month))

    return dues_payments, year_month_tuples


def generate_payable_months(catchup_months, subsequent_months):
    """
    Get the months the user can pay for.

    :param catchup_months: how many unpaid months in the past to include in the results
    :param subsequent_months: host many unpaid months in the future to include in the results
    :return: a list of tuples like ('2014-10', True) where the second element is True if the month is overdue or due
    """
    user_dues_payments, year_month_tuples = get_successful_dues_payments()

    this_month_date = datetime.datetime.utcnow().date()
    this_month_date = datetime.date(year=this_month_date.year, month=this_month_date.month, day=1)

    # Start generating from catchup_months ago
    start_date = this_month_date - relativedelta.relativedelta(months=catchup_months)

    # If the member signed up more recently than that, start at the signup month
    signup_date = datetime.date(year=current_user.member_signup.year, month=current_user.member_signup.month, day=1)
    if signup_date > start_date:
        start_date = signup_date

    # Generate the number required, skipping paid months
    i = 0
    payable_months = []
    while len(payable_months) < subsequent_months:
        future_month = start_date + relativedelta.relativedelta(months=i)
        i += 1

        if (future_month.year, future_month.month) not in year_month_tuples:
            due = True if future_month <= this_month_date else False
            payable_months.append((future_month.strftime('%Y-%m'), due))

    return payable_months


@app.route('/users/wepay_dues')
@login_required
def users_wepay_dues():
    paid_periods = DuesPaymentPeriod.query \
        .join(DuesPayment) \
        .filter_by(user_id=current_user.id, void=False) \
        .all()

    # Retain only those without exceptions
    paid_periods = filter(lambda p: p.dues_payment.exception is None, paid_periods)

    # Take just the most recent ones (at the end)
    recent_paid_periods = sorted(paid_periods, key=lambda p: (p.year, p.month))[-6:]

    if current_user.member_type:
        monthly_dues = format_currency(current_user.member_type.currency, current_user.member_type.monthly_dues)
        payable_months = generate_payable_months(2, 6)
    else:
        monthly_dues = None
        payable_months = []

    return render_template('/users/wepay_dues.html',
                           monthly_dues=monthly_dues,
                           recent_paid_periods=recent_paid_periods,
                           payable_months=payable_months,
                           utcnow=datetime.datetime.utcnow())


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

    months = request.args.getlist('month', None)
    if not months:
        return 'Missing month parameter(s)', 403

    # Set of integer (year, month) tuples
    month_tuples = set()
    try:
        month_datetimes = [datetime.datetime.strptime(m, '%Y-%m') for m in months]
        month_tuples = [(dt.year, dt.month) for dt in month_datetimes]
    except ValueError as err:
        return 'Error parsing month: %s' % (str(err)), 403

    num_months = len(month_tuples)
    if num_months < 1:
        return 'You have to pay for at least 1 month', 403

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
        wepay_dues_payment = create_dues_payment(checkout, month_tuples)
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