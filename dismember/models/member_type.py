from dismember.currency import format_currency
from dismember.models.model_mixins import DetailsMixin
from sqlalchemy import Numeric, Column, Integer, Text
from sqlalchemy.orm import relationship

from dismember.service import db


class MemberType(db.Model, DetailsMixin):
    """A membership type or level (none, full, associate, etc.)"""
    __tablename__ = 'member_types'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    # Support more than a single currency?
    monthly_dues = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(Text, nullable=False)

    users = relationship('User', backref='member_type')

    def __str__(self):
        return self.name

    @property
    def details(self):
        return [format_currency(self.currency, self.monthly_dues)]


