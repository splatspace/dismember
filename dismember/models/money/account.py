from sqlalchemy import text
from sqlalchemy.schema import *
from sqlalchemy.types import *
from sqlalchemy.orm import *

from dismember.service import db, cookie_serializer, config


class Account(db.Model):
    """
    An account that can be credited or debited to show changes in financial position relative
    to some other account.
    """
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    account_type = Column(Enum('asset', 'liability', 'equity', 'income', 'expense', name='account_type'), index=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))

    def __str__(self):
        return self.name

    def is_debit_account(self):
        """
        Get whether a debit (instead of a credit) is typically used to increase the value of this account.
        Some account types are traditionally called "debit accounts" for this reason.

        :return: True if a debit increases the value of this account, False if a credit increases the value of this account
        """
        # http://en.wikipedia.org/wiki/Debits_and_credits#The_five_accounting_elements
        return self.account_type in ('asset', 'expenses')