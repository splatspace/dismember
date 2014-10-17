import datetime

from dismember.service import db
from flask.ext.security import RoleMixin
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class DuesPaymentPeriod(db.Model):
    __tablename__ = 'dues_payment_periods'

    id = Column(Integer, primary_key=True)
    dues_payment_id = Column(ForeignKey('dues_payments.id'), nullable=False)
    # dues_payment (backref)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    def __str__(self):
        return '{:04d}-{:02d}'.format(self.year, self.month)

    @property
    def date(self):
        """Get a datetime at the start of the period."""
        return datetime.datetime.strptime('%d-%d' % (self.year, self.month), '%Y-%m')
