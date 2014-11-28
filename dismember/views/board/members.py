from dismember.dues import dues_service
from dismember.members import member_service
from flask import render_template

from dismember.service import app
from flask.ext.login import login_required
from flask.ext.security import roles_required


@app.route('/board/members')
@login_required
@roles_required('board')
def board_members():
    users = member_service.get_members()
    users = sorted(users, key=lambda u: (u.full_name, u.email))

    most_recent_dues_payments = {}
    for user in users:
        all_dues_payments = dues_service.get_dues_payments(user)

        # Get all the periods covered by all the payments
        paid_periods = []
        for dues_payment in all_dues_payments:
            paid_periods.extend(dues_payment.periods)

        sorted_paid_periods = sorted(paid_periods, key=lambda p: (p.year, p.month))
        if len(sorted_paid_periods) == 0:
            continue

        # Take just the most recent payment
        most_recent_dues_payments[user] = sorted_paid_periods[-1]

    return render_template('/board/members.html',
                           members=users,
                           most_recent_dues_payments=most_recent_dues_payments)
