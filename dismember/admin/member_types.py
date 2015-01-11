from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.member_type import MemberType
from dismember.models.role import Role
from dismember.wtforms_components.forms import DismemberModelForm
from wtforms.validators import DataRequired, Optional
from wtforms_components import StringField, Unique, DecimalField, SelectField


class MemberTypesForm(DismemberModelForm):
    name = StringField(label='Name', validators=[
        DataRequired(),
        Unique(Role.name, message='That role name is already in use')
    ])

    description = StringField(label='Description', validators=[
        Optional()
    ])

    monthly_dues = DecimalField(label='Monthly Dues', validators=[
        DataRequired(),
    ])

    # The data model accepts any ISO abbreviation, but US dollars are probably the only
    # reasonable choice for now.
    currency = SelectField(label='Currency', choices=[('USD', 'US Dollars ($)')], validators=[
        DataRequired(),
    ])


member_types_view = configure_crud_view(admin_bp, 'member_types', MemberType, MemberTypesForm, MemberTypesForm,
                                        'member type', 'member types', MemberType.name)
