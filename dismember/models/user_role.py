from peewee import ForeignKeyField
from dismember.models.role import Role
from dismember.models.user import User

from dismember.service import db


class UserRole(db.Model):
    """Joins Users to Roles"""

    class Meta:
        db_table = 'users_roles'

        # Defining this as a primary key trips up Flask-Security's Peewee datastore when
        # it creates users with roles.  Using a plain old unique index works, though.
        # primary_key = CompositeKey('user', 'role')

        indexes = (
            (('role', 'user'), True),
        )

    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)


UserRole.create_table(fail_silently=True)
