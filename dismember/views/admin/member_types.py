from flask.ext.admin.contrib.sqla import ModelView

from dismember.service import db, admin
from dismember.models.member_type import MemberType


class MemberTypesView(ModelView):
    column_list = ('name', 'description', 'monthly_dues')

    def __init__(self, **kwargs):
        super(MemberTypesView, self).__init__(MemberType, db.session, **kwargs)

admin.add_view(MemberTypesView(name='Member Types'))