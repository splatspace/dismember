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


def get_recent_dues_payments(count):
    return DuesPayment.query.filter_by(id=current_user.id).order_by(DuesPayment.created.desc()).limit(count).all()


def create_dues_payments_for_checkout(checkout, start_month, months):
    wepay_dues_payments = []
    for i in range(0, months):
        future_month = start_month + relativedelta.relativedelta(months=i)

        # Check for non-void payments of any type that conflict with the year and month
        existing_payment = DuesPayment.query.filter_by(user_id=current_user.id, void=False,
                                                       period_year=future_month.year,
                                                       period_month=future_month.month).first()

        # Ignore payments in "exception" (we'll assume a manual approval was given to re-pay for that period).
        if existing_payment and existing_payment.exception is None:
            raise ValueError(
                'You have already made a dues payment for the month of {:04d}-{:02d}.  '
                'Adjust the start month and number of months so this month is not included.'.format(
                    future_month.year, future_month.month))

        pmt = WePayDuesPayment()
        pmt.user_id = current_user.id
        pmt.period_year = future_month.year
        pmt.period_month = future_month.month
        pmt.wepay_checkout_id = checkout.id
        wepay_dues_payments.append(pmt)
    return wepay_dues_payments


@app.route('/users/wepay_dues')
@login_required
def users_wepay_dues():
    recent_payments = get_recent_dues_payments(12)
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

    start_month = request.args.get('start_month', None)
    if not start_month:
        return 'Missing start_month parameter', 403
    try:
        start_month = datetime.datetime.strptime(start_month, '%Y-%m')
    except ValueError as err:
        return 'Error parsing start month', 403

    months = request.args.get('months', 1)
    if not months:
        return 'Months not specified', 403
    try:
        months = int(months)
    except ValueError as err:
        return 'Error parsing month count', 403
    if months < 1:
        return 'You have to pay for at least 1 month', 403

    fee_payer = 'payee'
    if request.args.get('pay_fee', 'false') == 'true':
        fee_payer = 'payer'

    amount = current_user.member_type.monthly_dues * months

    checkout = WePayCheckout()
    checkout.account_id = app.config['WEPAY_ACCOUNT_ID']
    checkout.short_description = '%s dues (%d months)' % (app.config['DISMEMBER_ORG_NAME'], months)
    checkout.type = 'SERVICE'
    checkout.amount = str(amount)
    checkout.fee_payer = fee_payer
    checkout.callback_uri = url_for('users_wepay_dues_callback', _external=True)
    checkout.auto_capture = True
    db.session.add(checkout)

    # Create WePayDuesPayments for each dues period
    try:
        [db.session.add(p) for p in create_dues_payments_for_checkout(checkout, start_month, months)]
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