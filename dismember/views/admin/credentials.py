from dismember.models.prox_credential import ProxCredential
from flask.ext.admin.contrib.sqla import ModelView
from dismember.service import db, admin


class ProxCredentialsView(ModelView):
    excluded_form_columns = ('type',)

    def __init__(self, **kwargs):
        super(ProxCredentialsView, self).__init__(ProxCredential, db.session, **kwargs)


admin.add_view(ProxCredentialsView(name='HID Prox Fobs', category='Credentials'))