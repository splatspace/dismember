import datetime

from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, DecimalField
from dismember.models.currency import Currency
from dismember.models.payment_method import PaymentMethod
from dismember.service import db


class Payment(db.Model):
    """
    Money given to the organization, possibly in exchange for goods or services.  This class is
    intended to be subclassed for different types of payments (dues, donations, etc.).
    """

    # class Meta:
    # db_table = 'subclasses_must_define_the_table_name'

    id = PrimaryKeyField()
    method = ForeignKeyField(PaymentMethod)
    currency = ForeignKeyField(Currency)
    amount = DecimalField(max_digits=11, decimal_places=2)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return '%s' % self.currency.format(self.amount)