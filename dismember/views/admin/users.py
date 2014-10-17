from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin
from dismember.models.user import User


class UsersView(ModelView):
    can_create = False

    column_list = ('email', 'full_name', 'active')

    def __init__(self, **kwargs):
        super(UsersView, self).__init__(User, db.session, **kwargs)


admin.add_view(UsersView(name='Users'))