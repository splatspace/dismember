from sqlalchemy import Column, Integer, Text

from dismember.service import db
from sqlalchemy.orm import relationship


class ManualDuesPaymentType(db.Model):
    """A type of manual dues payment (cash, check, etc.)"""
    __tablename__ = 'manual_dues_payment_types'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    manual_dues_payment = relationship('ManualDuesPayment', backref='manual_dues_payment_type')

    def __str__(self):
        return self.name