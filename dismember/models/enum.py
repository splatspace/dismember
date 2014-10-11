import datetime

from flask.ext.peewee.admin import ModelAdmin

from peewee import PrimaryKeyField, TextField, DateTimeField
from dismember.service import db


class Enum(db.Model):
    """A basic enumeration model"""

    # class Meta:
    #     db_table = 'subclasses_must_define_the_table_name'

    id = PrimaryKeyField()
    name = TextField(unique=True)
    description = TextField(null=True)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name
