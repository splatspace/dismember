import datetime

from dismember.service import db
from sqlalchemy import Column, Integer, ForeignKey


class DuesPaymentPeriod(db.Model):
    __tablename__ = 'dues_payment_periods'

    id = Column(Integer, primary_key=True)
    dues_payment_id = Column(ForeignKey('dues_payments.id'), nullable=False)
    # dues_payment (backref)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    PERIOD_STRING_FORMAT = '%Y-%m'

    def __str__(self):
        return self.period_string

    @property
    def period_string(self):
        """Return a period string like '2014-10' for this object."""
        return self.start_date.strftime(DuesPaymentPeriod.PERIOD_STRING_FORMAT)

    @period_string.setter
    def period_string(self, value):
        """Set the year and month from a period string like '2014-10'"""
        dt = datetime.datetime.strptime(value, DuesPaymentPeriod.PERIOD_STRING_FORMAT)
        self.year = dt.year
        self.month = dt.month

    @staticmethod
    def from_period_string(period_string):
        """Create a new unmanaged DuesPaymentPeriod from a period string like '2014-10'"""
        period = DuesPaymentPeriod()
        period.period_string = period_string
        return period

    @staticmethod
    def to_period_string(date):
        """Format a date like '2014-10'"""
        return date.strftime(DuesPaymentPeriod.PERIOD_STRING_FORMAT)

    @property
    def start_date(self):
        """Get a date at the start of the period."""
        return datetime.date(self.year, self.month, 1)