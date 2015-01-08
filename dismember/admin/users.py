from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.user import User
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms_components import EmailField


class EditUserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User
        exclude = ['_password']

    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = PasswordField('Password (again)')


class NewUserForm(EditUserForm):
    class Meta(EditUserForm.Meta):
        exclude = EditUserForm.Meta.exclude + ['confirmed_at', 'last_login_at', 'current_login_at', 'last_login_ip',
                                               'current_login_ip', 'login_count']

    password = PasswordField(validators=[DataRequired(), EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = PasswordField('Password (again)')


users_view = configure_crud_view(admin_bp, 'users', User, NewUserForm, EditUserForm, 'user', 'users', User.full_name)
