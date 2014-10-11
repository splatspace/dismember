from dismember.models.wepay_checkout import WePayCheckout
from dismember.models.payment import Payment
from flask.ext.peewee.admin import ModelAdmin
from peewee import ForeignKeyField
from dismember.service import db


class WePayPayment(db.Model):
    """
    Links a WePayCheckout to a Payment.  A WePayCheckout may be linked to multiple Payment objects
    by using multiple WePayPayment objects.  This supports a scenario where a single
    WePayCheckout pays for a key deposit and first months' dues, which should be tracked separately.
    """

    class Meta:
        db_table = 'wepay_payments'

        # Defining this as a primary key trips up Flask-Security's Peewee datastore when
        # it creates users with roles. Using a plain old unique index works, though.
        # primary_key = CompositeKey('user', 'role')
        indexes = (
            (('checkout', 'payment'), True),
        )

    checkout = ForeignKeyField(WePayCheckout)
    payment = ForeignKeyField(Payment)

    def __str__(self):
        return '%s -> %s' % (self.checkout, self.payment)


class WePayPaymentAdmin(ModelAdmin):
    def get_display_name(self):
        return 'WePay Payments'

    def get_admin_name(self):
        return 'wepay_payments'


WePayPayment.create_table(fail_silently=True)

