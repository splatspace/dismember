import datetime

from flask import render_template, redirect, url_for, request
from dismember.service import app, auth
from dismember.models.dues_payment import DuesPayment
from dismember.wepay import wepay_service


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
               'is %s but WePay only supports USD' % user.member_type.currency, 403

    fee_payer = 'payee'
    if request.args.get('pay_fee', 'false') == 'true':
        fee_payer = 'payer'

    checkout = dict(
        account_id=app.config['WEPAY_ACCOUNT_ID'],
        short_description='%s dues payment' % (app.config['DISMEMBER_ORG_NAME']),
        type='SERVICE',
        amount=user.member_type.monthly_dues.amount,
        fee_payer=fee_payer,
        callback_uri=url_for('users_wepay_dues_callback'),
        auto_capture=True,
    )
    redirect_uri = url_for('users_wepay_dues_submit')
    return redirect(wepay_service.authorize_checkout(checkout, redirect_uri))


@app.route('/users/wepay_dues_submit')
@auth.login_required
def users_wepay_dues_submit():
    """
    Handle the second part of the WePay payment flow. This is where the user ends up after WePay finishes
    the flow started by users_wepay_dues_authorize.
    """

    redirect_uri = url_for('users_wepay_dues_submit')
    return redirect(wepay_service.authorize_checkout(checkout, redirect_uri))

@app.route('/users/wepay_dues_callback')
def users_wepay_dues_callback():
    """
    Handle an Instant Payment Notification: an asynchronous POST from WePay about a
    checkout that has changed state (authorized, settled, etc.). Expects the parameters
    that the WePay API docs state will be there.
    """
    checkout = request.get_json()
    wepay_service.refresh_checkout(checkout.checkout_id)
    return 'OK', 200