from flask.ext.peewee.admin import Admin

from flask.ext.peewee.auth import Auth
from dismember.models.user import UserAdmin, User


class DismemberAdmin(Admin):
    """A custom Admin that uses our custom models."""

    def check_user_permission(self, user):
        return user.has_role('Administrator')


class DismemberAuth(Auth):
    """A custom Auth that uses our custom ModelAdmin implementations"""

    def get_user_model(self):
        return User