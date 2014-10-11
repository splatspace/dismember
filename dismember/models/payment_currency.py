from flask.ext.peewee.admin import ModelAdmin

from dismember.models.enum import Enum
from peewee import TextField


class PaymentCurrency(Enum):
    """The currency used to make a payment (US Dollars, Bitcoin, etc.)"""

    class Meta:
        db_table = 'payment_currencies'

    symbol = TextField()

    def __str__(self):
        return '%s (%s)' % (self.name, self.symbol)

    def format(self, amount):
        return '%s%s' % (self.symbol, amount)


class PaymentCurrencyAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Payment Currencies'

    def get_admin_name(self):
        return 'payment_currencies'


PaymentCurrency.create_table(fail_silently=True)