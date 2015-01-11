from dismember.dues import dues_service
from dismember.user import user_bp
from flask import render_template

from flask.ext.login import login_required, current_user


@user_bp.route('/dues_history', methods=['GET'])
@login_required
def dues_history():
    all_dues_payments = dues_service.get_dues_payments(current_user, include_void=True, include_exceptional=True)

    # Get all the periods covered by all the payments
    paid_periods = []
    for dues_payment in all_dues_payments:
        paid_periods.extend(dues_payment.periods)

    # Order by date, reversed
    sorted_paid_periods = sorted(paid_periods, key=lambda p: (p.year, p.month), reverse=True)

    return render_template('/user/dues_history.html', paid_periods=sorted_paid_periods)

