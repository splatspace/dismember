from flask.ext.peewee.admin import ModelAdmin
from dismember.models.enum import Enum


class PaymentType(Enum):
    """A type of payment made to the organization (donation, dues, reservation, etc.)"""

    class Meta:
        db_table = 'payment_types'


class PaymentTypeAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Payment Types'

    def get_admin_name(self):
        return 'payment_types'


PaymentType.create_table(fail_silently=True)