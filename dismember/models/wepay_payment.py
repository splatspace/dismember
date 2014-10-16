from dismember.models.dues_payment import DuesPayment
from dismember.models.wepay_checkout import WePayCheckout
from dismember.service import db
from dismember.models.payment import Payment
from sqlalchemy import Integer, Column
from sqlalchemy.sql.schema import ForeignKey


class WePayPayment(db.Model):
    """Links a WePayCheckout to a Payment (probably one of its subclasses)."""

    __tablename__ = 'wepay_payments'

    # Composite primary key
    wepay_checkout = Column(Integer, ForeignKey(WePayCheckout.id), primary_key=True)
    payment_id = Column(Integer, ForeignKey(Payment.id), primary_key=True)

    def __str__(self):
        return '%s -> %s' % (self.wepay_checkout, self.dues_payment)