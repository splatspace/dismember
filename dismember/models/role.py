import datetime

from flask.ext.peewee.admin import ModelAdmin

from peewee import PrimaryKeyField, TextField, DateTimeField
from dismember.service import db


class Role(db.Model):
    """A system or business access role (admin, service, etc.)"""

    class Meta:
        db_table = 'roles'

    id = PrimaryKeyField()
    name = TextField(unique=True)
    description = TextField(null=True)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name


class RoleAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Roles'

    def get_admin_name(self):
        return 'roles'


Role.create_table(fail_silently=True)