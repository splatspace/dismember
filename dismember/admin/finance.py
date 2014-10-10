from flask.ext.admin.contrib.sqla.filters import *
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.superadmin.model.base import prettify

from dismember.models.money.transaction import Transaction

from dismember.service import admin, db
from dismember.models.money.account import Account


class AccountsModelView(ModelView):
    column_list = ('name', 'account_type', 'description')
    column_searchable_list = ('name', 'description')
    form_columns = ('name', 'description', 'account_type', 'created_at')

    def __init__(self, **kwargs):
        super(AccountsModelView, self).__init__(Account, db.session, **kwargs)


class TransactionsModelView(ModelView):
    column_list = ('time', 'debit_account', 'credit_account', 'amount', 'description')
    form_columns = ('time', 'debit_account', 'credit_account', 'amount', 'description')

    column_searchable_list = ('description', Account.name)

    column_filters = (
        FilterEqual(Transaction.amount, 'Amount'),
        FilterGreater(Transaction.amount, 'Amount'),
        FilterSmaller(Transaction.amount, 'Amount')
    )

    column_default_sort = 'time'

    def __init__(self, **kwargs):
        super(TransactionsModelView, self).__init__(Transaction, db.session, **kwargs)


# Add in the order they should appear
admin.add_view(TransactionsModelView(category='Finance', name='Transactions'))
admin.add_view(AccountsModelView(category='Finance', name='Accounts'))
