from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.member_type import MemberType
from dismember.models.role import Role
from dismember.models.user import User
from dismember.service import app
from dismember.wtforms_components.fields import DateTimeWithTimeZoneField
from dismember.wtforms_components.forms import DismemberModelForm
from wtforms import PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Optional
from wtforms_components import EmailField, Unique, StringField

password_field = lambda required=False: PasswordField(validators=[
    DataRequired() if required else Optional(),
    EqualTo('password_confirm', message='Passwords must match')
])
password_confirm_field = lambda: PasswordField('Password (again)')


class EditUserForm(DismemberModelForm):
    email = EmailField(label='E-mail Address', validators=[
        DataRequired(),
        Unique(User.email, message='That e-mail address is assigned to another user')
    ])

    full_name = StringField(label='Full Name', validators=[
        DataRequired(),
    ])

    address = StringField(label='Address', validators=[
        DataRequired(),
    ])

    phone = StringField(label='Phone', validators=[
        DataRequired(),
    ])

    emergency_contact = StringField(label='Emergency Contact', validators=[
        DataRequired(),
    ])

    member_signup = DateTimeWithTimeZoneField(label='Membership Approval Date',
                                              tzinfo=app.config['DISMEMBER_UI_TIMEZONE'])

    member_type = QuerySelectField(label='Member Type', query_factory=lambda: MemberType.query.all(), allow_blank=True)

    roles = QuerySelectMultipleField(label='Roles', query_factory=lambda: Role.query.all(), allow_blank=True)

    # Optional on edit
    password = password_field(False)
    password_confirm = password_confirm_field()


class NewUserForm(EditUserForm):
    # Required on new
    password = password_field(True)
    password_confirm = password_confirm_field()


users_view = configure_crud_view(admin_bp, 'users', User, NewUserForm, EditUserForm, 'user', 'users',
                                 User.full_name)
