from dismember.service import db
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
    created = Column(DateTime, nullable=False, server_default=text('now()'))
    void = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'payment',
        'polymorphic_on': type
    }

    @property
    def paid_amount(self):
        """Get the amount that was paid.  This value may change over time (charge backs to credit cards, etc.)"""
        return None

    @property
    def paid_currency(self):
        """Get the currency abbreviation used for the payment."""
        return None

    @property
    def paid_amount_str(self):
        """Get a formatted string describing the paid amount in the paid currency."""
        return None

    @property
    def payment_type(self):
        """Get a user-friendly string that describes the payment type (cash, check, WePay, etc.)"""
        return None

    @property
    def payer_reference(self):
        """Get an ID that the payer can correlate with their method of payment (check number, CC transaction, cash receipt number, etc.)"""
        return None

    @property
    def exception(self):
        """
        Get a string describing any exceptional conditions that apply to this payment.

        :return: a string describing the exception or None if there is no exception
        """
        return None