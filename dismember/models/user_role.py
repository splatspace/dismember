from peewee import ForeignKeyField, CompositeKey
from dismember.models.role import Role
from dismember.models.user import User

from dismember.service import db


class UserRole(db.Model):
    """Joins Users to Roles"""

    class Meta:
        db_table = 'users_roles'
        # Defining this primary key trips up Flask-Security's Peewee datastore when
        # it creates users with roles.  Leaving it out for now.
        # primary_key = CompositeKey('user', 'role')

    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)

UserRole.create_table(fail_silently=True)
