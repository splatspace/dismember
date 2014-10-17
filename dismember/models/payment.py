from dismember.service import db
from dismember.models.utils import *
from sqlalchemy import Column, Integer, Text, DateTime, text


class Payment(db.Model):
    """
    Money given to the organization, possibly in exchange for goods or services.  This class is
    intended to be subclassed for different types of payments (dues, donations, etc.) using
    joined table inheritance.
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)

    currency = Column(Text, nullable=False)
    amount = money_column()
    created = Column(DateTime, nullable=False, server_default=text('now()'))

    __mapper_args__ = {
        'polymorphic_identity': 'payment',
        'polymorphic_on': type
    }

    def __str__(self):
        return '%s' % self.currency.format(self.amount)