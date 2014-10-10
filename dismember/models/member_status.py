import datetime

from peewee import PrimaryKeyField, TextField, DateTimeField
from dismember.service import db


class MemberStatus(db.Model):
    """Status of membership (active, inactive, suspended, revoked, terminated, etc.)."""

    class Meta:
        db_table = 'member_statuses'

    id = PrimaryKeyField()
    name = TextField(unique=True)
    description = TextField(null=True)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name


MemberStatus.create_table(fail_silently=True)