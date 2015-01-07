from dismember.service import db
from dismember.wtforms_alchemy.fields import DateTimeWithTimeZoneField
from flask.ext.wtf import Form
from sqlalchemy import DateTime
from wtforms_alchemy import model_form_factory, ClassMap


class TimeZoneAwareFieldMeta:
    """A form Meta class that declares a type map that enables time-zone aware field controls."""
    type_map = ClassMap((
        (DateTime, DateTimeWithTimeZoneField),
    ))


class SessionModelForm(model_form_factory(Form)):
    """Extends WTForms-Alchemy's enhanced ModelForm to provide a database session."""

    @classmethod
    def get_session(cls):
        return db.session


