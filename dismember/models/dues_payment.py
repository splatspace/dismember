from dismember.models.payment import Payment
from dismember.models.user import User
from sqlalchemy import Integer, Column, ForeignKey


class DuesPayment(Payment):
    """A Payment for dues for exactly one dues period."""

    __tablename__ = 'dues_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # user (backref)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'dues_payment'
    }

    def __str__(self):
        return '@{:04d}-{:02d}'.format(self.period_year, self.period_month)