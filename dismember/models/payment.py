import datetime
from dateutil.tz import tzutc
from dismember.service import db
from pytz import utc
from sqlalchemy import Column, Integer, Text, DateTime, text, Boolean


class Payment(db.Model):
    """
    Something of value given to the organization, possibly in exchange for goods or services.
    This class is intended to be subclassed for different types of payments (dues,
    donations, etc.) using joined table inheritance.
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(utc))
    void = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'payment',
        'polymorphic_on': type
    }

    @property
    def visible(self):
        """Get whether this payment should be visible to users."""
        raise NotImplementedError()

    @property
    def charged_amount(self):
        """Get the amount that was originally charged.  This value will not change even if the payment is refunded."""
        raise NotImplementedError()

    @property
    def paid_amount(self):
        """Get the amount that was paid.  This value may change over time (charge backs to credit cards, etc.)"""
        raise NotImplementedError()

    @property
    def paid_currency(self):
        """Get the currency abbreviation used for the payment."""
        raise NotImplementedError()

    @property
    def payment_method(self):
        """Get a user-friendly string that describes the payment method (cash, check, WePay, etc.)"""
        raise NotImplementedError()

    @property
    def payer_reference(self):
        """Get an ID that the payer can correlate with their method of payment (check number, CC transaction, cash receipt number, etc.)"""
        raise NotImplementedError()

    @property
    def exception(self):
        """
        Get a string describing any exceptional conditions that apply to this payment.

        :return: a string describing the exception or None if there is no exception
        """
        raise NotImplementedError()