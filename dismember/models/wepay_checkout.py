from flask.ext.peewee.admin import ModelAdmin
from dismember.service import db
from peewee import PrimaryKeyField, TextField, IntegerField, DecimalField, Check, BooleanField


class WePayCheckout(db.Model):
    """
    A WePay checkout (the transaction type that gives us money), either in-progress or
    completed.  HTTP callbacks from WePay inform us of changes in state as they happen.
    This object essentially mirrors the state from the WePay service.  A checkout
    is recognized as a payment by creating a Payment object, then linking it to the
    WePayCheckout through a WePayPayment.

    https://www.wepay.com/developer/reference/checkout
    """

    class Meta:
        db_table = 'wepay_checkouts'

    PaymentMethodName = 'WePay'

    id = PrimaryKeyField()

    # Not all of the WePay API Checkout properties are present in this class.  We just
    # track the ones we might want to query on locally.

    # WePay (required for create)
    account_id = IntegerField()
    short_description = TextField()
    type = TextField(constraints=[Check("type in ('GOODS', 'SERVICE', 'DONATION', 'EVENT', 'PERSONAL')")])
    amount = DecimalField(max_digits=10, decimal_places=2)
    
    # WePay (optional for create)
    currency = TextField(null=True)
    long_description = TextField(null=True)
    payer_email_message = TextField(null=True)
    payee_email_message = TextField(null=True)
    reference_id = TextField(null=True)
    app_fee = DecimalField(null=True, max_digits=10, decimal_places=2)
    fee_payer = TextField(null=True,
                          constraints=[Check("type in (null, 'payer', 'payee', 'payer_from_app', 'payee_from_app')")])
    redirect_uri = TextField(null=True)
    callback_uri = TextField(null=True)
    auto_capture = BooleanField(null=True)

    # WePay (updated by callbacks)
    checkout_id = IntegerField(null=True)
    payer_name = TextField(null=True)
    payer_email = TextField(null=True)
    state = TextField(null=True)
    gross = DecimalField(null=True, max_digits=10, decimal_places=2)
    fee = DecimalField(null=True, max_digits=10, decimal_places=2)
    amount_refunded = DecimalField(null=True, max_digits=10, decimal_places=2)
    amount_charged_back = DecimalField(null=True, max_digits=10, decimal_places=2)

    def __str__(self):
        # Hard-code dollars for WePay
        return '$%s (%s <%s>)' % (self.amount, self.payer_name, self.payer_email)


class WePayCheckoutAdmin(ModelAdmin):
    def get_display_name(self):
        return 'WePay Checkouts'

    def get_admin_name(self):
        return 'wepay_checkouts'


WePayCheckout.create_table(fail_silently=True)

