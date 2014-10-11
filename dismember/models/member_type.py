from flask.ext.peewee.admin import ModelAdmin

from dismember.models.enum import Enum


class MemberType(Enum):
    """A membership type or level (none, full, associate, etc.)"""

    class Meta:
        db_table = 'member_types'


class MemberTypeAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Member Types'

    def get_admin_name(self):
        return 'member_types'


MemberType.create_table(fail_silently=True)