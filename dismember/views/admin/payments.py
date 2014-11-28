from dismember.models.dues_payment import DuesPayment
from dismember.models.payment import Payment
from dismember.models.wepay_dues_payment import WePayDuesPayment
from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin


class PaymentsView(ModelView):
    can_create = False

    # column_list = ('email', 'full_name', 'active')

    def __init__(self, **kwargs):
        super(PaymentsView, self).__init__(WePayDuesPayment, db.session, **kwargs)


admin.add_view(PaymentsView(name='Payments'))