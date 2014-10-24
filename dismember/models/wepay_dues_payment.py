from dismember.models.dues_payment import DuesPayment
from dismember.models.wepay_checkout import WePayCheckout
from dismember.models.wepay_payment_mixin import WePayPaymentMixin
from sqlalchemy import Integer, Column
from sqlalchemy.sql.schema import ForeignKey


class WePayDuesPayment(WePayPaymentMixin, DuesPayment):
    """A dues payment made through WePay."""

    __tablename__ = 'wepay_dues_payments'

    id = Column(Integer, ForeignKey('dues_payments.id'), primary_key=True)

    wepay_checkout_id = Column(Integer, ForeignKey(WePayCheckout.id), index=True, nullable=False)
    # wepay_checkout (backref)

    __mapper_args__ = {
        'polymorphic_identity': 'wepay_dues_payment'
    }

    def __str__(self):
        return '%s %s (WePay)' % (super(WePayDuesPayment, self).__str__(), self.wepay_checkout)
