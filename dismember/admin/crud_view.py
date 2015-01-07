from dismember.wtforms_alchemy.model_form import SessionModelForm
from dismember.service import db, app
from flask import url_for, render_template, request, redirect
from flask.views import MethodView
from wtforms import DateTimeField
from wtforms.ext.sqlalchemy.orm import model_form, ModelConverter, converts




# class CRUDConverter(ModelConverter):
#     @converts('DateTime')
#     def conv_DateTime(self, field_args, **extra):
#         if extra['column'].type.timezone:
#             return DateTimeWithTimeZoneField(tzinfo=app.config['DISMEMBER_UI_TIMEZONE'], **field_args)
#         else:
#             return DateTimeField(**field_args)


# class CRUDView(MethodView):
#     def __init__(self, model, endpoint, list_template=None, view_template=None):
#         self.model = model
#         self.endpoint = endpoint
#         self.path = url_for('.%s' % self.endpoint)
#         self.list_template = list_template or 'list.html'
#         self.view_template = view_template or 'view.html'
#
#     # def get(self):
#     # obj = self.model.query.all()
#     # return render_template(self.list_template, obj=obj, path=self.path)
#
#     def _create_model_form_cls(self):
#         return SessionModelForm()
#         return model_form(self.model, db.session, converter=CRUDConverter())
#
#     def get(self, obj_id=''):
#         if obj_id:
#             # this creates the form fields base on the model
#             # so we don't have to do them one by one
#             model_form_cls = self._create_model_form_cls()
#
#             obj = self.model.query.get(obj_id)
#             form = model_form_cls(obj=obj)
#
#             action = request.path
#             return render_template(self.view_template, form=form, path=self.path, action=action)
#
#         obj = self.model.query.order_by(self.model.created_at.desc()).all()
#         return render_template(self.list_template, obj=obj, path=self.path)
#
#     def post(self, obj_id=''):
#         if obj_id:
#             obj = self.model.query.get(obj_id)
#         else:
#             obj = self.model
#
#         model_form_cls = self._create_model_form_cls()
#         form = model_form_cls(request.form)
#         form.populate_obj(obj)
#
#         db.session.add(obj)
#         db.session.commit()
#
#         return redirect(self.path)