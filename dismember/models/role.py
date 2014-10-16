from dismember.service import db
from flask.ext.security import RoleMixin
from sqlalchemy import Column, Integer, Text


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    # Flask-Security required
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, index=True, nullable=False)
    description = Column(Text)

    def __str__(self):
        return self.name