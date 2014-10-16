from flask.ext.peewee.admin import ModelAdmin
from dismember.models.dues_payment import DuesPayment
from dismember.models.wepay_checkout import WePayCheckout
from peewee import ForeignKeyField
from dismember.service import db


class WePayDuesPayment(db.Model):
    """Links a WePayCheckout to a DuesPayment."""

    class Meta:
        db_table = 'wepay_dues_payments'

    dues_payment = ForeignKeyField(DuesPayment)
    wepay_checkout = ForeignKeyField(WePayCheckout)

    def __str__(self):
        return '%s -> %s' % (self.wepay_checkout, self.dues_payment)


class WePayDuesPaymentAdmin(ModelAdmin):
    def get_display_name(self):
        return 'WePay Dues Payments'

    def get_admin_name(self):
        return 'wepay_dues_payments'


WePayDuesPayment.create_table(fail_silently=True)