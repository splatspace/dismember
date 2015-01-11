from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.role import Role
from dismember.models.user import User
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta
from wtforms import PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Optional
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_components import EmailField, Unique, read_only

email_field = lambda: EmailField(validators=[
    DataRequired(),
    Unique(User.email, message='That e-mail address is assigned to another user')
])

roles_field = lambda: QuerySelectMultipleField(query_factory=lambda: Role.query.all(), allow_blank=True)
                                               # widget=ListWidget(), option_widget=CheckboxInput())

password_field = lambda required=False: PasswordField(validators=[
    DataRequired() if required else Optional(),
    EqualTo('password_confirm', message='Passwords must match')
])

password_confirm_field = lambda: PasswordField('Password (again)')


class NewUserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User
        exclude = ['_password', 'confirmed_at', 'last_login_at', 'current_login_at', 'last_login_ip',
                   'current_login_ip', 'login_count']

    email = email_field()
    roles = roles_field()

    # Required on new
    password = password_field(True)
    password_confirm = password_confirm_field()


class EditUserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User
        exclude = ['_password']

    email = email_field()
    roles = roles_field()

    # Optional on edit
    password = password_field(False)
    password_confirm = password_confirm_field()

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        read_only(self.confirmed_at)
        read_only(self.current_login_at)
        read_only(self.current_login_ip)
        read_only(self.last_login_at)
        read_only(self.last_login_ip)
        read_only(self.login_count)


users_view = configure_crud_view(admin_bp, 'users', User, NewUserForm, EditUserForm, 'user', 'users',
                                 User.full_name)
