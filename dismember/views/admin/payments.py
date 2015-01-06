from dismember.models.wepay_dues_payment import WePayDuesPayment
from dismember.views.custom_fields import DateTimeWithTimeZoneField
from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin, app


class PaymentsView(ModelView):
    can_create = False

    # column_list = ('email', 'full_name', 'active')

    form_overrides = dict(
        created_at=DateTimeWithTimeZoneField,
    )

    form_args = dict(
        created_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
    )

    def __init__(self, **kwargs):
        super(PaymentsView, self).__init__(WePayDuesPayment, db.session, **kwargs)


admin.add_view(PaymentsView(name='Payments'))