from dismember.models.dues_payment import DuesPayment
from dismember.models.manual_dues_payment import ManualDuesPayment
from dismember.models.wepay_dues_payment import WePayDuesPayment
from dismember.views.custom_fields import DateTimeWithTimeZoneField
from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin, app


class AllDuesPaymentsView(ModelView):
    can_create = False

    column_list = ('created_at', 'user', 'periods', 'paid_amount_str', 'payment_type', 'exception')
    excluded_form_columns = ('type',)

    form_overrides = dict(
        created_at=DateTimeWithTimeZoneField,
    )

    form_args = dict(
        created_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
    )

    def __init__(self, **kwargs):
        super(AllDuesPaymentsView, self).__init__(DuesPayment, db.session, **kwargs)


admin.add_view(AllDuesPaymentsView(name='All', category='Dues Payments'))


class WePayDuesPaymentsView(ModelView):
    can_create = False

    column_list = ('created_at', 'user', 'periods', 'paid_amount_str', 'exception', 'wepay_checkout')
    excluded_form_columns = ('type',)

    form_overrides = dict(
        created_at=DateTimeWithTimeZoneField,
    )

    form_args = dict(
        created_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
    )

    def __init__(self, **kwargs):
        super(WePayDuesPaymentsView, self).__init__(WePayDuesPayment, db.session, **kwargs)


admin.add_view(WePayDuesPaymentsView(name='WePay', category='Dues Payments'))


class ManualDuesPaymentsView(ModelView):
    column_list = ('created_at', 'user', 'periods', 'paid_amount_str', 'exception', 'manual_dues_payment_type')
    excluded_form_columns = ('type', 'periods')

    form_overrides = dict(
        created_at=DateTimeWithTimeZoneField,
    )

    form_args = dict(
        created_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
    )

    def __init__(self, **kwargs):
        super(ManualDuesPaymentsView, self).__init__(ManualDuesPayment, db.session, **kwargs)

    def create_form(self, obj=None):
        form = super(ManualDuesPaymentsView, self).create_form(obj)
        if form.currency.data is None:
            form.currency.data = app.config['DISMEMBER_DEFAULT_CURRENCY']
        return form


admin.add_view(ManualDuesPaymentsView(name='Manual', category='Dues Payments'))

