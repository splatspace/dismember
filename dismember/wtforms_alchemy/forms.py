from dismember.service import db
from dismember.wtforms_alchemy.fields import DateTimeWithTimeZoneField
from flask.ext.wtf import Form
from sqlalchemy import DateTime
from wtforms_alchemy import model_form_factory, FormGenerator
from wtforms_components import DateTimeField


class TimeZoneAwareFormGenerator(FormGenerator):
    def get_field_class(self, column):
        if isinstance(column.type, DateTime):
            if column.type.timezone:
                return DateTimeWithTimeZoneField
            else:
                return DateTimeField
        return super(TimeZoneAwareFormGenerator, self).get_field_class(column)


class TimeZoneAwareFieldMeta(object):
    """A form Meta class that declares a type map that enables time-zone aware field controls."""

    form_generator = TimeZoneAwareFormGenerator


class SessionModelForm(model_form_factory(Form)):
    """Extends WTForms-Alchemy's enhanced ModelForm to provide a database session."""

    @classmethod
    def get_session(cls):
        return db.session


