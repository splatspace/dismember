from flask.ext.peewee.admin import ModelAdmin

from dismember.models.enum import Enum
from dismember.models.currency import Currency
from peewee import DecimalField, ForeignKeyField


class MemberType(Enum):
    """A membership type or level (none, full, associate, etc.)"""

    class Meta:
        db_table = 'member_types'

    # Support more currencies?
    monthly_dues = DecimalField(max_digits=11, decimal_places=2)
    currency = ForeignKeyField(Currency)


class MemberTypeAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Member Types'

    def get_admin_name(self):
        return 'member_types'


MemberType.create_table(fail_silently=True)