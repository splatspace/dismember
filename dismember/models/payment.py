import datetime

from flask.ext.peewee.admin import ModelAdmin
from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, DecimalField
from dismember.models.currency import Currency
from dismember.models.payment_method import PaymentMethod
from dismember.models.payment_type import PaymentType
from dismember.service import db


class Payment(db.Model):
    """Money given to the organization, possibly in exchange for goods or services."""

    class Meta:
        db_table = 'payments'

    id = PrimaryKeyField()
    method = ForeignKeyField(PaymentMethod)
    type = ForeignKeyField(PaymentType)
    currency = ForeignKeyField(Currency)
    amount = DecimalField(max_digits=11, decimal_places=2)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return '#%s (%s)' % (self.id, self.currency.format(self.amount))


class PaymentAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Payments'

    def get_admin_name(self):
        return 'payments'


Payment.create_table(fail_silently=True)