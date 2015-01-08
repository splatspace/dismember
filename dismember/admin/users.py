from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.user import User
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms_components import EmailField, Unique


class EditUserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User
        exclude = ['_password', 'confirmed_at', 'last_login_at', 'current_login_at', 'last_login_ip',
                   'current_login_ip', 'login_count']

    email = EmailField(validators=[DataRequired(),
                                   Unique(User.email, message='That e-mail address is assigned to another user')])
    password = PasswordField(validators=[EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = PasswordField('Password (again)')


class NewUserForm(EditUserForm):
    password = PasswordField(validators=[DataRequired(), EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = PasswordField('Password (again)')


users_view = configure_crud_view(admin_bp, 'users', User, NewUserForm, EditUserForm, 'user', 'users', User.full_name)
