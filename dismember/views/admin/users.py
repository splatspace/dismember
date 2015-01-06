from dismember.models.prox_credential import ProxCredential
from dismember.views.custom_fields import DateTimeWithTimeZoneField
from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin, app
from dismember.models.user import User


class UsersView(ModelView):
    can_create = False

    column_list = ('email', 'full_name', 'active')

    form_overrides = dict(
        created_at=DateTimeWithTimeZoneField,
        member_signup=DateTimeWithTimeZoneField,
    )

    form_args = dict(
        created_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
        member_signup=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
    )

    def __init__(self, **kwargs):
        super(UsersView, self).__init__(User, db.session, **kwargs)


admin.add_view(UsersView(name='List', category='Users'))


class ProxCredentialsView(ModelView):
    excluded_form_columns = ('type',)
    column_exclude_list = ('type',)

    def __init__(self, **kwargs):
        super(ProxCredentialsView, self).__init__(ProxCredential, db.session, **kwargs)


admin.add_view(ProxCredentialsView(name='HID Prox Fob Credentials', category='Users'))