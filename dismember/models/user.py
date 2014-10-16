from dismember.models.member_type import MemberType
from dismember.service import db
from flask.ext.security import UserMixin
from dismember.models.role import Role
from dismember.models.utils import *
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

users_roles = Table(
    'users_roles',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id', onupdate='cascade', ondelete='cascade')),
    Column('role_id', Integer, ForeignKey('roles.id', onupdate='cascade', ondelete='cascade'))
)


class User(db.Model, UserMixin):
    """A human or other being authorized to use this application."""
    __tablename__ = 'users'

    # Flask-Security required
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    roles = relationship(Role, secondary=users_roles)

    # Flask-Security optional
    confirmed_at = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))
    current_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(Text)
    current_login_ip = Column(Text)
    login_count = Column(Integer)

    # Our fields
    created = datetime_tz_default_now()
    full_name = Column(Text, nullable=False)

    # Membership information
    member_signup = Column(DateTime(timezone=True))
    member_type_id = Column(Integer, ForeignKey(MemberType.id))
    address = Column(Text)
    phone = Column(Text)
    emergency_contact = Column(Text)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __str__(self):
        return '%s (%s)' % (self.email, self.full_name)
