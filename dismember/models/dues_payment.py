from dismember.models.payment import Payment
from dismember.models.user import User
from dismember.models.utils import *
from sqlalchemy import Integer, Column, ForeignKey


class DuesPayment(Payment):
    """A Payment for dues."""

    __tablename__ = 'dues_payments'

    id = Column(Integer, ForeignKey(Payment.id), primary_key=True)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    period_begin = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))

    __mapper_args__ = {
        'polymorphic_identity': 'dues_payment'
    }

    def __str__(self):
        return '%s (%s: %s to %s)' % (
            super(DuesPayment, self).__str__(), self.user.full_name, self.period_begin, self.period_end)