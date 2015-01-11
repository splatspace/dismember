from dismember.donations import donation_service
from dismember.user import user_bp
from flask import render_template

from flask.ext.login import login_required, current_user


@user_bp.route('/donation_history', methods=['GET'])
@login_required
def donation_history():
    payments = donation_service.get_donation_payments(current_user, include_void=True, include_exceptional=True)

    # Order by date, reversed
    payments = sorted(payments, key=lambda p: p.created_at, reverse=True)

    return render_template('/user/donation_history.html', payments=payments)

