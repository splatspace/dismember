from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.prox_credential import ProxCredential
from dismember.models.user import User
from dismember.wtforms_components.forms import DismemberModelForm
from wtforms import BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from wtforms_components import IntegerField


class ProxCredentialForm(DismemberModelForm):
    user = QuerySelectField(label='User', query_factory=lambda: User.query.all(), allow_blank=False)

    number = IntegerField(label='Number', description='The internal authentication code', validators=[
        DataRequired()
    ])

    enabled = BooleanField(label='Enabled', description='', validators=[
        DataRequired(),
    ], default=True)


prox_credentials_view = configure_crud_view(admin_bp, 'prox_credentials', ProxCredential, ProxCredentialForm,
                                            ProxCredentialForm, 'HID Prox credential', 'HID Prox credentials',
                                            ProxCredential.number)
