import datetime

from dateutil import relativedelta
from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, current_user
from dismember.service import app, db
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service
from dismember.models.wepay_checkout import WePayCheckout
from dismember.models.wepay_dues_payment import WePayDuesPayment
from dismember.views.template_helpers import format_currency


def create_dues_payments_for_checkout(checkout, month_tuples):
    """
    Create a WePayDuesPayment for each month tuple specified.

    :param checkout: the WePayCheckout to link the payments to
    :param month_tuples: iterable of integer (year, month) tuples
    :return: a list of WePayDuesPayments
    """
    wepay_dues_payments = []
    for (year, month) in month_tuples:
        # Check for non-void payments of any type that conflict with the year and month
        existing_payment = DuesPayment.query.filter_by(user_id=current_user.id, void=False,
                                                       period_year=year,
                                                       period_month=month).first()

        # Ignore payments in "exception" (we'll assume a manual approval was given to re-pay for that period).
        if existing_payment and existing_payment.exception is None:
            raise ValueError(
                'You have already made a dues payment for the month of {:04d}-{:02d}.  '
                'Adjust the start month and number of months so this month is not included.'.format(
                    year, month))

        pmt = WePayDuesPayment()
        pmt.user_id = current_user.id
        pmt.period_year = year
        pmt.period_month = month
        pmt.wepay_checkout_id = checkout.id
        wepay_dues_payments.append(pmt)
    return wepay_dues_payments


def generate_payable_months(subsequent_months):
    # Order these from most recent to oldest
    user_dues_payments = DuesPayment.query \
        .filter_by(user_id=current_user.id, void=False) \
        .order_by(DuesPayment.period_year.desc(), DuesPayment.period_month.desc()) \
        .all()

    # Retain only those without exceptions
    user_dues_payments = filter(lambda p: p.exception is None, user_dues_payments)

    # Extract (year, month) tuples for easy searching
    paid_year_months = set([(p.period_year, p.period_month) for p in user_dues_payments])

    # Determine where to start generating the list of months
    if user_dues_payments:
        # Start one past the last payment
        start_month = user_dues_payments[-1].period_date + relativedelta.relativedelta(months=1)
    else:
        # Start now
        start_month = datetime.datetime.utcnow()

    # Generate the number required, skipping paid months
    i = 0
    payable_months = []
    while len(payable_months) < subsequent_months:
        future_month = start_month + relativedelta.relativedelta(months=i)
        i += 1

        if (future_month.year, future_month.month) not in paid_year_months:
            payable_months.append(future_month.strftime('%Y-%m'))

    return payable_months


@app.route('/users/wepay_dues')
@login_required
def users_wepay_dues():
    # Get some recent dues payments
    recent_dues_payments = DuesPayment.query \
        .filter_by(user_id=current_user.id, void=False) \
        .order_by(DuesPayment.period_year, DuesPayment.period_month) \
        .all()

    # Retain only those without exceptions, and just take the last few
    recent_dues_payments = filter(lambda p: p.exception is None, recent_dues_payments)

    # And just take the most recent ones (at the end)
    recent_dues_payments = recent_dues_payments[-6:]

    if current_user.member_type:
        monthly_dues = format_currency(current_user.member_type.currency, current_user.member_type.monthly_dues)
        payable_months = generate_payable_months(6)
    else:
        monthly_dues = None
        payable_months = []

    return render_template('/users/wepay_dues.html',
                           monthly_dues=monthly_dues,
                           recent_dues_payments=recent_dues_payments,
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
        [db.session.add(p) for p in create_dues_payments_for_checkout(checkout, month_tuples)]
    except ValueError as err:
        return str(err), 403

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