from dismember.admin import admin_bp
from dismember.crud.views.crud_view import CrudView
from dismember.models.role import Role
from dismember.wtforms_components.forms import DismemberModelForm
from wtforms.validators import DataRequired
from wtforms_components import StringField, Unique


class RoleForm(DismemberModelForm):
    name = StringField(label='Name', validators=[
        DataRequired(),
        Unique(Role.name, message='That member type name is already in use')
    ])

    description = StringField(label='Description', validators=[
        DataRequired(),
    ])


crud_view = CrudView(admin_bp, 'roles', Role, RoleForm, RoleForm, 'Role', "Roles", Role.name)
