from flask.ext.peewee.admin import AdminModelConverter
from dismember.custom_fields import DateTimeWithTimeZoneField
from dismember.service import admin

# Replace the form converter with one that can handle our custom field types
from wtforms import DateTimeField


# class RememberModelConverter(AdminModelConverter):
#     def __init__(self, *args, **kwargs):
#         super(RememberModelConverter, self).__init__(*args, additional={DateTimeWithTimeZoneField: DateTimeField})
#
# admin.form_converter = RememberModelConverter

# Import in the order they should appear in the menu
import users
