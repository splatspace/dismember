# Replace the form converter with one that can handle our custom field types


# class RememberModelConverter(AdminModelConverter):
# def __init__(self, *args, **kwargs):
#         super(RememberModelConverter, self).__init__(*args, additional={DateTimeWithTimeZoneField: DateTimeField})
#
# admin.form_converter = RememberModelConverter

# Import in the order they should appear in the menu
import users
