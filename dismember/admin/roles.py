from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.role import Role
from dismember.wtforms_components.forms import DismemberModelForm
from wtforms.validators import DataRequired
from wtforms_components import StringField, Unique, ModelForm


class RoleForm(DismemberModelForm):
    name = StringField(label='Name', validators=[
        DataRequired(),
        Unique(Role.name, message='That role name is already in use')
    ])

    description = StringField(label='Description', validators=[
        DataRequired(),
    ])


roles_view = configure_crud_view(admin_bp, 'roles', Role, RoleForm, RoleForm, 'role', 'roles', Role.name)
