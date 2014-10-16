from flask.ext.peewee.admin import ModelAdmin

from peewee import PrimaryKeyField, TextField, IntegerField, DecimalField, Check, BooleanField, DateTimeField

from dismember.models.utils import to_dict
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
    cancel_reason = TextField(null=True)
    checkout_id = IntegerField(null=True)
    create_time = DateTimeField(null=True)
    dispute_uri = TextField(null=True)
    payer_name = TextField(null=True)
    payer_email = TextField(null=True)
    soft_descriptor = TextField(null=True)
    state = TextField(null=True)
    gross = money_field(null=True)
    fee = money_field(null=True)
    amount_refunded = money_field(null=True)
    amount_charged_back = money_field(null=True)
    refund_reason = TextField(null=True)
    shipping_address = TextField(null=True)

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

    def update(self, checkout):
        """Update the model from a dictionary of WePay API properties"""

        if self.reference_id != checkout['reference_id']:
            raise ValueError('The reference ID cannot be changed; possible object mismatch')

        self.checkout_id = checkout['checkout_id']
        self.account_id = checkout['account_id']
        self.preapproval_id = checkout['preapproval_id']
        self.create_time = checkout['create_time']
        self.state = checkout['state']
        self.soft_descriptor = checkout['soft_descriptor']
        self.short_description = checkout['short_description']
        self.long_description = checkout['long_description']
        self.currency = checkout['currency']
        self.amount = checkout['amount']
        self.shipping_fee = checkout['shipping_fee']
        self.fee = checkout['fee']
        self.gross = checkout['gross']
        self.app_fee = checkout['app_fee']
        self.amount_refunded = checkout['amount_refunded']
        self.amount_charged_back = checkout['amount_charged_back']
        self.fee_payer = checkout['fee_payer']
        self.redirect_uri = checkout['redirect_uri']
        self.callback_uri = checkout['callback_uri']
        self.dispute_uri = checkout['dispute_uri']
        self.payer_email = checkout['payer_email']
        self.payer_name = checkout['payer_name']
        self.cancel_reason = checkout['cancel_reason']
        self.refund_reason = checkout['refund_reason']
        self.auto_capture = checkout['auto_capture']
        self.require_shipping = checkout['require_shipping']
        self.shipping_address = checkout['shipping_address']
        self.mode = checkout['mode']


class WePayCheckoutAdmin(ModelAdmin):
    def get_display_name(self):
        return 'WePay Checkouts'

    def get_admin_name(self):
        return 'wepay_checkouts'


WePayCheckout.create_table(fail_silently=True)

