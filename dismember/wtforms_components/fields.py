from dateutil.parser import parse
from pytz import timezone
from wtforms_components import DateTimeField


def remove_empty_password_fields(form):
    """Removes empty password fields from the form so those fields will not be updated in the model."""
    for field in form:
        if field.type == 'PasswordField' and field.data == '':
            del form[field.name]


def encrypt_password_fields(form, item, encrypt_func):
    for field in form:
        if field.type == 'PasswordField':
            encrypted = encrypt_func(form[field.name].data)
            setattr(item, field.name, encrypted)


class DateTimeWithTimeZoneField(DateTimeField):
    """A DateTimeField that always parses timezone aware Python datetimes."""

    def __init__(self, label=None, validators=None, display_format=None, tzinfo=None, **kwargs):
        """
            :param display_format:
                A strftime format string used when displaying datetimes. Defaults to '%Y-%m-%d %H:%M:%S %Z'
            :param tzinfo:
                The time zone used when displaying naive datetimes and as the default time zone
                when a parsed datetime does not specify a timezone.  Defaults to UTC.
        """
        super(DateTimeWithTimeZoneField, self).__init__(label, validators, **kwargs)

        self._display_format = display_format or '%Y-%m-%d %H:%M:%S %Z'
        self._tzinfo = tzinfo or timezone('UTC')

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            if self.data:
                dt = self.data
                if self.data.tzinfo is None:
                    dt = self._tzinfo.localize(self.data)
                return dt.strftime(self._display_format)
            else:
                return ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            if date_str.strip() == '':
                self.data = None
            else:
                try:
                    self.data = parse(date_str)
                    # If no time zone was parsed use the default
                    if self.data.tzinfo is None:
                        self.data = self._tzinfo.localize(self.data)
                except (ValueError, TypeError):
                    self.data = None
                    raise ValueError(self.gettext('Not a valid datetime value'))
