from flask.ext.peewee.admin import ModelAdmin

from peewee import PrimaryKeyField, TextField, IntegerField, DecimalField, Check, BooleanField

from dismember.models import to_dict
from dismember.service import db


def money_field(null=False, **kwargs):
    # 10 total digits, 2 digits to the right of the decimal point, lets us hold
    # up to 99,999,999.99.
    return DecimalField(null=null, max_digits=10, decimal_places=2, **kwargs)


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

    # Fields required for /checkout/create
    account_id = IntegerField()
    short_description = TextField()
    type = TextField(constraints=[Check("type in ('GOODS', 'SERVICE', 'DONATION', 'EVENT', 'PERSONAL')")])
    amount = money_field()

    # Fields optional for /checkout/create
    currency = TextField(null=True)
    long_description = TextField(null=True)
    payer_email_message = TextField(null=True)
    payee_email_message = TextField(null=True)
    reference_id = TextField(null=True)
    app_fee = money_field(null=True)
    fee_payer = TextField(null=True,
                          constraints=[Check("type in (null, 'payer', 'payee', 'payer_from_app', 'payee_from_app')")])
    redirect_uri = TextField(null=True)
    callback_uri = TextField(null=True)
    fallback_uri = TextField(null=True)
    auto_capture = BooleanField(null=True)
    require_shipping = BooleanField(null=True)
    shipping_fee = money_field(null=True)
    mode = TextField(null=True)
    preapproval_id = IntegerField(null=True)
    # prefill_info = foreign key to a prefill table?
    funding_sources = TextField(null=True)
    payment_method_id = IntegerField(null=True)
    payment_method_type = TextField(null=True)

    # Fields updated from return values or by callbacks
    checkout_id = IntegerField(null=True)
    payer_name = TextField(null=True)
    payer_email = TextField(null=True)
    state = TextField(null=True)
    gross = money_field(null=True)
    fee = money_field(null=True)
    amount_refunded = money_field(null=True)
    amount_charged_back = money_field(null=True)

    def __str__(self):
        # Hard-code dollars for WePay
        return '$%s (%s <%s>)' % (self.amount, self.payer_name, self.payer_email)

    def to_create_dict(self):
        """Get a dictionary with only the values that are valid for /checkout/create"""
        return to_dict(self, [
            'account_id',
            'short_description',
            'type',
            'amount',
            'currency',
            'long_description',
            'payer_email_message',
            'payee_email_message',
            'reference_id',
            'app_fee',
            'fee_payer',
            'redirect_uri',
            'callback_uri',
            'fallback_uri',
            'auto_capture',
            'require_shipping',
            'shipping_fee',
            'mode',
            'preapproval_id',
            'prefill_info',
            'funding_sources',
            'payment_method_id',
            'payment_method_type'], include_none_values=False)


class WePayCheckoutAdmin(ModelAdmin):
    def get_display_name(self):
        return 'WePay Checkouts'

    def get_admin_name(self):
        return 'wepay_checkouts'


WePayCheckout.create_table(fail_silently=True)

