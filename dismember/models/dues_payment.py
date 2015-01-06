import datetime

from dismember.models.payment import Payment
from sqlalchemy import Integer, Column, ForeignKey
from sqlalchemy.orm import relationship


class DuesPayment(Payment):
    """A Payment for dues for exactly one dues period."""

    __tablename__ = 'dues_payments'

    id = Column(Integer, ForeignKey('payments.id', onupdate='cascade', ondelete='cascade'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), nullable=False)
    # user (backref)
    periods = relationship('DuesPaymentPeriod', cascade='all, delete-orphan', backref='dues_payment')

    __mapper_args__ = {
        'polymorphic_identity': 'dues_payment'
    }

    def __str__(self):
        return ','.join([str(period) for period in self.periods])
