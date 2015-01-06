from dismember.views.custom_fields import DateTimeWithTimeZoneField
from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin, app
from dismember.models.user import User


class UsersView(ModelView):
    can_create = False

    column_list = ('email', 'full_name', 'active')

    form_overrides = dict(
        created_at=DateTimeWithTimeZoneField,
        confirmed_at=DateTimeWithTimeZoneField,
        last_login_at=DateTimeWithTimeZoneField,
        current_login_at=DateTimeWithTimeZoneField,
        member_signup=DateTimeWithTimeZoneField,
    )

    form_args = dict(
        created_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
        confirmed_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
        last_login_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
        current_login_at=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
        member_signup=dict(tzinfo=app.config['DISMEMBER_UI_TIMEZONE']),
    )

    def __init__(self, **kwargs):
        super(UsersView, self).__init__(User, db.session, **kwargs)


admin.add_view(UsersView(name='Users'))