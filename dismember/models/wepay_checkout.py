from dismember.currency import money_column, format_currency
from sqlalchemy import Text, Integer, Enum, Boolean, BigInteger, Column

from dismember.service import db
from dismember.models.utils import *
from sqlalchemy.orm import relationship


class WePayCheckout(db.Model):
    """
    A WePay checkout (the transaction type that gives us money), either in-progress or
    completed.  HTTP callbacks from WePay inform us of changes in state as they happen.
    This object essentially mirrors the state from the WePay service.  A checkout
    is recognized as a payment by creating a Payment object, then linking it to the
    WePayCheckout through a WePayPayment.

    https://www.wepay.com/developer/reference/checkout
    """

    __tablename__ = 'wepay_checkouts'

    id = Column(Integer, primary_key=True)

    # Not all of the WePay API Checkout properties are present in this class.  We just
    # track the ones we might want to query on locally.

    # Fields required for /checkout/create
    account_id = Column(Integer, nullable=False)
    short_description = Column(Text, nullable=False)
    type = Column(Enum('GOODS', 'SERVICE', 'DONATION', 'EVENT', 'PERSONAL', name='wepay_checkout_type'))
    amount = money_column()

    # Fields optional for /checkout/create
    currency = Column(Text)
    long_description = Column(Text)
    payer_email_message = Column(Text)
    payee_email_message = Column(Text)
    reference_id = Column(Text)
    app_fee = money_column(nullable=True)
    fee_payer = Column(Enum('payer', 'payee', 'payer_from_app', 'payee_from_app', name='wepay_checkout_fee_payer'),
                       nullable=True)
    redirect_uri = Column(Text)
    callback_uri = Column(Text)
    fallback_uri = Column(Text)
    auto_capture = Column(Boolean)
    require_shipping = Column(Boolean)
    shipping_fee = money_column(nullable=True)
    mode = Column(Text)
    preapproval_id = Column(Integer)
    # prefill_info = foreign key to a prefill table?
    funding_sources = Column(Text)
    payment_method_id = Column(Integer)
    payment_method_type = Column(Text)

    # Fields updated from return values or by callbacks
    cancel_reason = Column(Text)
    checkout_id = Column(Integer)
    create_time = Column(BigInteger)
    dispute_uri = Column(Text)
    payer_name = Column(Text)
    payer_email = Column(Text)
    soft_descriptor = Column(Text)
    state = Column(Text)
    gross = money_column(nullable=True)
    fee = money_column(nullable=True)
    amount_refunded = money_column(nullable=True)
    amount_charged_back = money_column(nullable=True)
    refund_reason = Column(Text)
    shipping_address = Column(Text)

    wepay_dues_payments = relationship('WePayDuesPayment', backref='wepay_checkout')
    wepay_donation_payments = relationship('WePayDonationPayment', backref='wepay_checkout')

    def __str__(self):
        return '%s (%s <%s>)' % (format_currency('USD', self.amount), self.payer_name, self.payer_email)

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
            'payment_method_type'], include_none_values=False, stringify=['amount', 'app_fee', 'shipping_fee'])

    def update_from_dict(self, checkout):
        """
        Update the model from a dictionary of WePay API properties.

        This object's properties will be set to None if the dictionary either contains a value
        of None for that property or does not contain the property at all.
        """

        if self.reference_id != checkout['reference_id']:
            raise ValueError('The reference ID cannot be changed; possible object mismatch')

        self.checkout_id = checkout.get('checkout_id', None)
        self.account_id = checkout.get('account_id', None)
        self.preapproval_id = checkout.get('preapproval_id', None)
        self.create_time = checkout.get('create_time', None)
        self.state = checkout.get('state', None)
        self.soft_descriptor = checkout.get('soft_descriptor', None)
        self.short_description = checkout.get('short_description', None)
        self.long_description = checkout.get('long_description', None)
        self.currency = checkout.get('currency', None)
        self.amount = checkout.get('amount', None)
        self.shipping_fee = checkout.get('shipping_fee', None)
        self.fee = checkout.get('fee', None)
        self.gross = checkout.get('gross', None)
        self.app_fee = checkout.get('app_fee', None)
        self.amount_refunded = checkout.get('amount_refunded', None)
        self.amount_charged_back = checkout.get('amount_charged_back', None)
        self.fee_payer = checkout.get('fee_payer', None)
        self.redirect_uri = checkout.get('redirect_uri', None)
        self.callback_uri = checkout.get('callback_uri', None)
        self.dispute_uri = checkout.get('dispute_uri', None)
        self.payer_email = checkout.get('payer_email', None)
        self.payer_name = checkout.get('payer_name', None)
        self.cancel_reason = checkout.get('cancel_reason', None)
        self.refund_reason = checkout.get('refund_reason', None)
        self.auto_capture = checkout.get('auto_capture', None)
        self.require_shipping = checkout.get('require_shipping', None)
        self.shipping_address = checkout.get('shipping_address', None)
        self.mode = checkout.get('mode', None)

