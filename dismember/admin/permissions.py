from flask.ext.admin.contrib.sqla import ModelView
from wtforms import ValidationError

from dismember.models.role import Role

from dismember.service import admin, db, config


class RolesModelView(ModelView):
    can_create = True

    def __init__(self, **kwargs):
        super(RolesModelView, self).__init__(Role, db.session, **kwargs)

    def on_model_delete(self, model):
        if model.name == config['adminRole']['name']:
            raise ValidationError('Cannot delete the "%s" role.' % model.name)

# Add in the order they should appear
admin.add_view(RolesModelView(category='Permissions', name='Roles'))
