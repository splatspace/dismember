from flask.ext.peewee.admin import ModelAdmin
from dismember.service import db
from peewee import PrimaryKeyField, TextField


class WePayCheckout(db.Model):
    """
    A WePay checkout (the transaction type that gives us money), either in-progress or
    completed.  HTTP callbacks from WePay inform us of changes in state as they happen.
    This object essentially mirrors the state from the WePay service.  A checkout
    is recognized as a payment by creating a Payment object, then linking it to the
    WePayCheckout through a WePayPayment.
    """

    class Meta:
        db_table = 'wepay_checkouts'

    PaymentMethodName = 'WePay'

    id = PrimaryKeyField()
    foo = TextField()
    # method = ForeignKeyField(PaymentMethod)
    # type = ForeignKeyField(PaymentType)
    # currency = ForeignKeyField(PaymentCurrency)
    # amount = DecimalField(max_digits=11, decimal_places=2)
    # created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return '#%s (%s)' % (self.id, self.foo)


class WePayCheckoutAdmin(ModelAdmin):
    def get_display_name(self):
        return 'WePay Checkouts'

    def get_admin_name(self):
        return 'wepay_checkouts'


WePayCheckout.create_table(fail_silently=True)

