from dismember.currency import format_currency


class WePayPaymentMixin(object):
    """Implements methods required by Payment that are common to all types of WePay payments."""

    @property
    def visible(self):
        # The state will be None if the user never finished the WePay web flow
        return self.wepay_checkout.state is not None

    @property
    def charged_amount(self):
        return self.wepay_checkout.amount

    @property
    def paid_amount(self):
        amount = self.wepay_checkout.amount or 0
        refunded_gross = self.wepay_checkout.amount_refunded or 0
        charged_back_gross = self.wepay_checkout.amount_charged_back or 0

        # amount_refunded and amount_charged_back are a gross amounts.  We must manually
        # compute the net amounts to exclude the service fee if there was a refund or charge back.
        refunded_net = refunded_gross
        charged_back_net = charged_back_gross
        if self.wepay_checkout.fee_payer == 'payer':
            if refunded_net > 0:
                refunded_net = refunded_net - self.wepay_checkout.fee
            if charged_back_net > 0:
                charged_back_net = charged_back_net - self.wepay_checkout.fee

        return amount - refunded_net - charged_back_net

    @property
    def paid_currency(self):
        return self.wepay_checkout.currency

    @property
    def payment_method(self):
        return 'WePay'

    @property
    def payer_reference(self):
        return self.wepay_checkout.checkout_id

    @property
    def exception(self):
        # Chargebacks are always exceptional
        if self.wepay_checkout.amount_charged_back > 0:
            return 'Charge back %s from %s gross leaves net %s' % (
                format_currency(self.paid_currency, self.wepay_checkout.amount_charged_back),
                format_currency(self.paid_currency, self.wepay_checkout.gross),
                format_currency(self.paid_currency, self.paid_amount))

        # Refunds are always exceptional
        if self.wepay_checkout.amount_refunded > 0:
            return 'Refund of %s from %s gross leaves net %s' % (
                format_currency(self.paid_currency, self.wepay_checkout.amount_refunded),
                format_currency(self.paid_currency, self.wepay_checkout.gross),
                format_currency(self.paid_currency, self.paid_amount))

        # These probably indicate a problem
        if self.wepay_checkout.state in [None, 'new', 'failed', 'cancelled', 'charged back', 'refunded', 'expired']:
            return 'Checkout state is %s' % self.wepay_checkout.state

        return None
