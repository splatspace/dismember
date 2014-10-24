import datetime

from dateutil import relativedelta
from dismember.models.dues_payment import DuesPayment
from dismember.models.dues_payment_period import DuesPaymentPeriod


class DuesService(object):
    """
    Provides high-level methods for managing member dues.
    """

    def get_dues_payments(self, user, include_void=False, include_exceptional=False):
        """
        Get all dues payments made by a user.

        :param user: the user to search for dues payments from
        :param include_void: if True payments marked as void will be included in the results, if False they will not
        :param include_exceptional: if True payments with a non-None exceptional property will be included in the
            results, if False they will not
        :return: an iterable of DuesPayments
        """
        query = DuesPayment.query.filter_by(user_id=user.id)
        if not include_void:
            query = query.filter_by(void=False)
        dues_payments = query.all()

        if not include_exceptional:
            dues_payments = filter(lambda p: p.exception is None, dues_payments)

        return dues_payments

    def generate_payable_periods(self, user, past_periods=2, future_periods=6):
        """
        Get a list of dues periods to suggest to the user.  Periods covered by a non-void, non-exceptional
        payment are not returned (because it would be silly to suggest the user pay it again).

        If the current month is unpaid, it is considered a past period and included with those
        results.

        Past periods before the user's member sign-up date are not included.

        :param past_periods: the number of unpaid past payment periods to consider including; this
            setting is a limit (up to the specified number may be included)
        :param future_periods: the number of unpaid future payment periods to include; exactly this many
            unpaid periods will be included
        :return: a list of unmanaged DuesPaymentPeriods for past periods, and a list of unmanaged
            DuesPaymentPeriods for future periods
        """
        this_month_date = datetime.datetime.utcnow().date()
        this_month_date = datetime.date(year=this_month_date.year, month=this_month_date.month, day=1)

        # Start searching from past_periods months ago
        start_date = this_month_date - relativedelta.relativedelta(months=past_periods)

        # If the member signed up more recently than that, start at the signup month
        signup_date = datetime.date(year=user.member_signup.year, month=user.member_signup.month, day=1)
        if signup_date > start_date:
            start_date = signup_date

        # Compute all the paid periods as tuples so we can efficiently exclude those
        paid_period_tuples = set()
        for payment in self.get_dues_payments(user):
            for period in payment.periods:
                paid_period_tuples.add((period.year, period.month))

        # Generate the number required, skipping paid months
        past_payable_periods = []
        future_payable_periods = []
        i = 0
        while len(future_payable_periods) < future_periods:
            i_month = start_date + relativedelta.relativedelta(months=i)
            i += 1

            if (i_month.year, i_month.month) not in paid_period_tuples:
                period = DuesPaymentPeriod()
                period.year = i_month.year
                period.month = i_month.month
                if i_month <= this_month_date:
                    past_payable_periods.append(period)
                else:
                    future_payable_periods.append(period)

        return past_payable_periods, future_payable_periods


dues_service = DuesService()