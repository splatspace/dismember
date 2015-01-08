from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.role import Role
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta


class RoleForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = Role


roles_view = configure_crud_view(admin_bp, 'roles', Role, RoleForm, RoleForm, 'role', 'roles', Role.name)
