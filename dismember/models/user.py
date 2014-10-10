import datetime

from flask.ext.peewee.admin import ModelAdmin

from flask.ext.peewee.auth import BaseUser
from peewee import PrimaryKeyField, TextField, BooleanField, ForeignKeyField, DateTimeField
from dismember.models.member_status import MemberStatus
from dismember.models.member_type import MemberType
from dismember.service import db


class User(db.Model, BaseUser):
    """A human or other being authorized to use this application."""

    class Meta:
        db_table = 'users'

    # Fields required for Flask-Peewee's auth and admin features
    id = PrimaryKeyField()
    username = TextField(unique=True)
    email = TextField(unique=True, index=True)
    password = TextField()
    active = BooleanField(default=True)
    admin = BooleanField(default=True)

    # Our user properties
    full_name = TextField()
    created = DateTimeField(default=datetime.datetime.now)

    # Membership information
    member_signup = DateTimeField(null=True)
    member_type = ForeignKeyField(MemberType, null=True)
    member_status = ForeignKeyField(MemberStatus, null=True)
    address = TextField(null=True)
    phone = TextField(null=True)
    emergency_contact = TextField(null=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __str__(self):
        return '%s (%s)' % (self.username, self.full_name)

    @property
    def roles(self):
        return [ur.role for ur in self.user_roles]

    def has_role(self, role_name):
        return role_name in [r.name for r in self.roles]

    @property
    def admin(self):
        """Required by AdminAuthentication"""
        return self.has_role('Administrator')


class UserAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Users'

    def get_admin_name(self):
        return 'users'

    def save_model(self, instance, form, adding=False):
        # Ensure the password gets hashed correctly before it is stored in the database.
        orig_password = instance.password

        user = super(UserAdmin, self).save_model(instance, form, adding)

        if orig_password != form.password.data:
            user.set_password(form.password.data)
            user.save()

        return user


User.create_table(fail_silently=True)