from flask.ext.peewee.admin import ModelAdmin

from dismember.models.enum import Enum
from peewee import TextField


class Currency(Enum):
    """The currency used to make a payment (US Dollars, Bitcoin, etc.)"""

    class Meta:
        db_table = 'currencies'

    symbol = TextField()

    def __str__(self):
        return '%s (%s)' % (self.name, self.symbol)

    def format(self, amount):
        return '%s%s' % (self.symbol, amount)


class CurrencyAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Currencies'

    def get_admin_name(self):
        return 'currencies'


Currency.create_table(fail_silently=True)