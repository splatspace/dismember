from flask.ext.peewee.admin import ModelAdmin
from dismember.models.enum import Enum


class PaymentMethod(Enum):
    """A means of receiving payments (cash, check, WePay, etc.)"""

    class Meta:
        db_table = 'payment_methods'


class PaymentMethodAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Payment Methods'

    def get_admin_name(self):
        return 'payment_methods'


PaymentMethod.create_table(fail_silently=True)