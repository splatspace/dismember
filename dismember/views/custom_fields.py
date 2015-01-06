"""
Custom WTForms fields.
"""
from dateutil.parser import parse
from flask_admin.form.fields import DateTimeField
from pytz import utc, timezone


class DateTimeWithTimeZoneField(DateTimeField):
    def __init__(self, label=None, validators=None, format=None, tzinfo=None, **kwargs):
        """
            Constructor

            :param label:
                Label
            :param validators:
                Field validators
            :param format:
                Format for text to date conversion. Defaults to '%Y-%m-%d %H:%M:%S %Z'
            :param tzinfo:
                The time zone to display times in.  Defaults to UTC.
            :param kwargs:
                Any additional parameters
        """
        super(DateTimeWithTimeZoneField, self).__init__(label, validators, **kwargs)

        self.format = format or '%Y-%m-%d %H:%M:%S %Z'
        self.tzinfo = tzinfo or timezone('UTC')

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            if self.data and self.data.tzinfo is None:
                self.data = self.tzinfo.localize(self.data)
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = parse(date_str)
                # If no time zone was parsed use the default
                if self.data.tzinfo is None:
                    self.data = self.tzinfo.localize(self.data)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid datetime value'))