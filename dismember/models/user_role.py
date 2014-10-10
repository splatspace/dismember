from peewee import ForeignKeyField, CompositeKey
from remember.models.role import Role
from remember.models.user import User

from remember.service import db


class UserRole(db.Model):
    """Joins Users to Roles"""

    class Meta:
        db_table = 'user_roles'
        primary_key = CompositeKey('user', 'role')

    user = ForeignKeyField(User, related_name='user_roles')
    role = ForeignKeyField(Role, related_name='role_users')


UserRole.create_table(fail_silently=True)
