from dismember.models.donation_payment import DonationPayment


class DonationService(object):
    """
    Provides high-level methods for managing donations.
    """

    def get_donation_payments(self, user=None, include_void=False, include_exceptional=False):
        """
        Get all donation payments made by a user.

        :param user: the user to search for donation payments from, or None to include non-user donations
        :param include_void: if True payments marked as void will be included in the results, if False they will not
        :param include_exceptional: if True payments with a non-None exceptional property will be included in the
            results, if False they will not
        :return: an iterable of DonationPayments
        """
        query = DonationPayment.query
        if user is not None:
            query = query.filter_by(user_id=user.id)
        if not include_void:
            query = query.filter_by(void=False)
        donation_payments = query.all()

        if not include_exceptional:
            donation_payments = filter(lambda p: p.exception is None, donation_payments)

        return donation_payments


donation_service = DonationService()