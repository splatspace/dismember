from dismember.service import db
from sqlalchemy import Column, Integer, Text
from sqlalchemy.sql.schema import ForeignKey


class Credential(db.Model):
    """A proof of identity or access for a user."""
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), nullable=False)
    # user (backref)

    type = Column(Text, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'credential',
        'polymorphic_on': type
    }

    def __str__(self):
        return self.type
