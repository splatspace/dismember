from dismember.service import db
from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

BaseModelForm = model_form_factory(Form)


class DismemberModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


