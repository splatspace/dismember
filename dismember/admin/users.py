from dismember.models.user import User
from dismember.service import db
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta
from flask import url_for, request, redirect, render_template
from flask.views import MethodView


class UserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User


class UserView(MethodView):
    def __init__(self, list_template=None, view_template=None):
        self.list_template = list_template or 'list.html'
        self.view_template = view_template or 'view.html'

    def get(self, obj_id=''):
        if obj_id:
            obj = User.query.get(obj_id)
            form = UserForm(obj=obj)

            action = request.path
            return render_template(self.view_template, form=form, path=url_for(request.endpoint), action=action)

        obj = User.query.order_by(User.full_name.desc()).all()
        return render_template(self.list_template, obj=obj, path=url_for(request.endpoint))

    def post(self, obj_id=''):
        if obj_id:
            obj = User.query.get(obj_id)
        else:
            obj = User

        form = UserForm(request.form)
        form.populate_obj(obj)

        db.session.add(obj)
        db.session.commit()

        return redirect(url_for(request.endpoint))