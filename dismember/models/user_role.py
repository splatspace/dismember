from peewee import ForeignKeyField, CompositeKey
from dismember.models.role import Role
from dismember.models.user import User

from dismember.service import db


class UserRole(db.Model):
    """Joins Users to Roles"""

    class Meta:
        db_table = 'users_roles'
        primary_key = CompositeKey('user', 'role')

    user = ForeignKeyField(User, related_name='user_roles')
    role = ForeignKeyField(Role, related_name='role_users')


UserRole.create_table(fail_silently=True)
