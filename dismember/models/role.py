import datetime

from peewee import PrimaryKeyField, TextField
from dismember.custom_fields import DateTimeWithTimeZoneField
from dismember.service import db


class Role(db.Model):
    """A system or business access role (admin, service, etc.)"""

    class Meta:
        db_table = 'roles'

    id = PrimaryKeyField()
    name = TextField(unique=True)
    description = TextField(null=True)
    created = DateTimeWithTimeZoneField(default=datetime.datetime.now)

    def __str__(self):
        return self.name


Role.create_table(fail_silently=True)