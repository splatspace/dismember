from flask.ext.peewee.admin import ModelAdmin, AdminModelConverter, AdminFilterModelConverter
from flask.ext.peewee.filters import FilterMapping
from dismember.custom_fields import DateTimeWithTimeZoneField
from dismember.service import admin
from dismember.models.user import User

# class MembersModelView(ModelView):
# column_labels = dict(
# email='Email',
# name='Name',
# active='Login Enabled')
#
# column_list = ('email', 'name', 'roles')
#     column_searchable_list = ('email', 'name')
#
#     # Don't show "password" (it would be encrypted); show the new_password* fields intead.
#     form_columns = (
#         'email',
#         'roles',
#         'name',
#         'new_password',
#         'new_password_2',
#         'active',
#         'membership_start',
#         'membership_type',
#         'membership_status',
#         'address',
#         'phone',
#         'emergency_contact',
#         'notes'
#     )
#     form_extra_fields = {
#         'new_password': PasswordField('Password', [EqualTo('new_password_2', 'The passwords must match')]),
#         'new_password_2': PasswordField('Password (Again)')
#     }
#
#     def __init__(self, **kwargs):
#         super(MembersModelView, self).__init__(Member, db.session, **kwargs)
#
#     def on_model_change(self, form, model, is_created):
#         model.password = encrypt_password(model.new_password)
#
#     def on_model_delete(self, model):
#         if model.has_role(config['adminRole']['name']):
#             raise ValidationError(
#                 'Cannot delete member "%s" because the "%s" role is assigned to it.  You must unassign '
#                 'this role before you can delete the member.' % (model.name, config['adminRole']['name']))
#
#
# # Add in the order they should appear
# admin.add_view(MembersModelView(name='Members'))

from wtfpeewee.fields import WPDateTimeField
from wtfpeewee.orm import FieldInfo


def shit(model, field, **kwargs):
    kwargs.pop('filters')
    return FieldInfo(field.name, WPDateTimeField(**kwargs))


class FooModelConverter(AdminModelConverter):
    def __init__(self, model_admin, **kwargs):
        kwargs['additional'] = {
            DateTimeWithTimeZoneField: shit
        }
        super(FooModelConverter, self).__init__(model_admin, **kwargs)


class FooFilterConverter(AdminFilterModelConverter):
    def __init__(self, model_admin, **kwargs):
        kwargs['additional'] = {
            DateTimeWithTimeZoneField: shit
        }
        super(FooFilterConverter, self).__init__(model_admin, **kwargs)


class FooFilterMapping(FilterMapping):
    def get_field_types(self):
        types = super(FooFilterMapping, self).get_field_types()
        types[DateTimeWithTimeZoneField] = 'datetime_date'
        return types


class FooAdmin(ModelAdmin):
    form_converter = FooModelConverter
    filter_converter = FooFilterConverter
    filter_mapping = FooFilterMapping


admin.register(User, admin_class=FooAdmin)
# admin.register(User)