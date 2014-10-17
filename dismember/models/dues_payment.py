from dismember.models.payment import Payment
from dismember.models.user import User
from sqlalchemy import Integer, Column, ForeignKey


class DuesPayment(Payment):
    """A Payment for dues for exactly one dues period."""

    __tablename__ = 'dues_payments'

    id = Column(Integer, ForeignKey(Payment.id), primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'dues_payment'
    }

    def __str__(self):
        return '{} {:4d}-{:2d}'.format(self.user.full_name, self.period_year, self.period_month)