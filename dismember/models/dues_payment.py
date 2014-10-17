import datetime

from dismember.models.payment import Payment
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
        return self.period_str

    @property
    def period_str(self):
        return '{:04d}-{:02d}'.format(self.period_year, self.period_month)

    @property
    def period_date(self):
        """Get a datetime at the start of the period."""
        return datetime.datetime.strptime('%d-%d' % (self.period_year, self.period_month), '%Y-%m')
