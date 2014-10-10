import datetime

from peewee import PrimaryKeyField, TextField
from remember.custom_fields import DateTimeWithTimeZoneField
from remember.service import db


class MemberType(db.Model):
    """A membership type or level (none, full, associate, etc.)"""

    class Meta:
        db_table = 'member_types'

    id = PrimaryKeyField()
    name = TextField(unique=True)
    description = TextField(null=True)
    created = DateTimeWithTimeZoneField(default=datetime.datetime.now)

    def __str__(self):
        return self.name


MemberType.create_table(fail_silently=True)