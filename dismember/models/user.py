import datetime

from dismember.models.member_type import MemberType
from dismember.models.model_mixins import DetailsMixin
from dismember.service import db
from flask.ext.security import UserMixin
from dismember.models.role import Role
from pytz import utc
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey


users_roles = Table(
    'users_roles',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id', onupdate='cascade', ondelete='cascade')),
    Column('role_id', Integer, ForeignKey('roles.id', onupdate='cascade', ondelete='cascade'))
)


class User(db.Model, UserMixin, DetailsMixin):
    """A human or other being authorized to use this application."""
    __tablename__ = 'users'

    # Flask-Security required
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    roles = relationship(Role, secondary=users_roles)

    # Flask-Security optional (naive UTC datetimes are used by Flask-Security, so don't use
    # time zones in the database or you'll get conversion errors).
    confirmed_at = Column(DateTime)
    last_login_at = Column(DateTime)
    current_login_at = Column(DateTime)
    last_login_ip = Column(Text)
    current_login_ip = Column(Text)
    login_count = Column(Integer)

    # Our fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(utc))
    full_name = Column(Text)

    # Membership information
    member_signup = Column(DateTime(timezone=True))
    member_type_id = Column(Integer, ForeignKey(MemberType.id, onupdate='cascade', ondelete='cascade'))
    # member_type (backref)
    address = Column(Text)
    phone = Column(Text)
    emergency_contact = Column(Text)

    dues_payments = relationship('DuesPayment', cascade='all, delete-orphan', backref='user')
    credentials = relationship('Credential', cascade='all, delete-orphan', backref='user')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.email

    @property
    def details(self):
        ret = [self.email]
        if not self.active:
            ret.append('account disabled')
        return ret
