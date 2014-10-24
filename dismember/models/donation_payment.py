import datetime

from dismember.models.payment import Payment
from sqlalchemy import Integer, Column, ForeignKey
from sqlalchemy.orm import relationship


class DonationPayment(Payment):
    """A Payment made as a donation."""

    __tablename__ = 'donation_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)

    # Optionally belongs to a user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    # user (backref)

    __mapper_args__ = {
        'polymorphic_identity': 'donation_payment'
    }
