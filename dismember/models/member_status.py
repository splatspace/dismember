from flask.ext.peewee.admin import ModelAdmin
from dismember.models.enum import Enum


class MemberStatus(Enum):
    """Status of membership (active, inactive, suspended, revoked, terminated, etc.)."""

    class Meta:
        db_table = 'member_statuses'


class MemberStatusAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Member Statuses'

    def get_admin_name(self):
        return 'member_statuses'


MemberStatus.create_table(fail_silently=True)