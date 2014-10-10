from sqlalchemy import text
from sqlalchemy.schema import *
from sqlalchemy.sql.functions import now
from sqlalchemy.types import *
from sqlalchemy.orm import *

from remember.service import db, cookie_serializer, config
from remember.models.money.account import Account


class Transaction(db.Model):
    """
    A financial transaction involving a debit to one account and a credit to another.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)

    debit_account_id = Column(Integer,
                              ForeignKey('accounts.id', onupdate='cascade', ondelete='restrict'),
                              index=True, nullable=False)
    debit_account = relationship(Account, foreign_keys=debit_account_id)

    credit_account_id = Column(Integer,
                               ForeignKey('accounts.id', onupdate='cascade', ondelete='restrict'),
                               index=True, nullable=False)
    credit_account = relationship(Account, foreign_keys=credit_account_id)

    amount = Column(Numeric(10, 2), CheckConstraint('amount > 0'), nullable=False)
    description = Column(Text, nullable=False)
    time = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
