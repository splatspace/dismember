import datetime

from flask import render_template
from dismember.service import app, auth
from dismember.models.dues_payment import DuesPayment


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