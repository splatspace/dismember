import datetime

from flask.ext.peewee.admin import ModelAdmin

from peewee import PrimaryKeyField, TextField, DateTimeField
from dismember.service import db


class MemberType(db.Model):
    """A membership type or level (none, full, associate, etc.)"""

    class Meta:
        db_table = 'member_types'

    id = PrimaryKeyField()
    name = TextField(unique=True)
    description = TextField(null=True)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name


class MemberTypeAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Member Types'

    def get_admin_name(self):
        return 'member_types'


MemberType.create_table(fail_silently=True)