from dismember.currency import money_column, format_currency
from dismember.models.dues_payment import DuesPayment
from dismember.models.manual_dues_payment_type import ManualDuesPaymentType
from sqlalchemy import Integer, Column, Text, Boolean
from sqlalchemy.sql.schema import ForeignKey


class ManualDuesPayment(DuesPayment):
    """A dues payment made by cash, check, or some other non-electronic means."""

    __tablename__ = 'manual_dues_payments'

    id = Column(Integer, ForeignKey('dues_payments.id', onupdate='cascade', ondelete='cascade'), primary_key=True)

    manual_dues_payment_type_id = Column(Integer,
                                         ForeignKey(ManualDuesPaymentType.id, onupdate='cascade', ondelete='cascade'),
                                         index=True, nullable=False)
    # manual_dues_payment_type (backref)

    currency = Column(Text, nullable=False)
    amount = money_column(nullable=False)
    reference = Column(Text)
    void = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'manual_dues_payment'
    }

    @property
    def charged_amount(self):
        return self.amount

    @property
    def paid_amount(self):
        return 0 if self.void else self.amount

    @property
    def paid_currency(self):
        return self.currency

    @property
    def paid_amount_str(self):
        return format_currency(self.paid_currency, self.paid_amount)

    @property
    def payment_method(self):
        return self.manual_dues_payment_type.name

    @property
    def payer_reference(self):
        return self.reference

    @property
    def exception(self):
        if self.void:
            return 'Voided'
        return None

    def __str__(self):
        return '%s (%s %s)' % (super(ManualDuesPayment, self).__str__(), self.payment_method, self.paid_amount_str)
