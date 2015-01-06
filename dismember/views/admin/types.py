from dismember.models.member_type import MemberType
from dismember.service import db

from dismember.models.manual_dues_payment_type import ManualDuesPaymentType
from flask.ext.admin.contrib.sqla import ModelView

from dismember.service import admin


class ManualDuesPaymentTypesView(ModelView):
    column_list = ('name', 'description')

    excluded_form_columns = ('manual_dues_payment',)

    def __init__(self, **kwargs):
        super(ManualDuesPaymentTypesView, self).__init__(ManualDuesPaymentType, db.session, **kwargs)


admin.add_view(ManualDuesPaymentTypesView(name='Manual Dues Payment Types', category='Types'))


class MemberTypesView(ModelView):
    column_list = ('name', 'description', 'monthly_dues')

    def __init__(self, **kwargs):
        super(MemberTypesView, self).__init__(MemberType, db.session, **kwargs)


admin.add_view(MemberTypesView(name='Member Types', category='Types'))