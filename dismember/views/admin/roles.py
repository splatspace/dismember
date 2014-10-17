from flask.ext.admin.contrib.sqla import ModelView

from dismember.service import db, admin
from dismember.models.role import Role


class RolesView(ModelView):
    column_list = ('name', 'description')

    def __init__(self, **kwargs):
        super(RolesView, self).__init__(Role, db.session, **kwargs)

admin.add_view(RolesView(name='Roles'))