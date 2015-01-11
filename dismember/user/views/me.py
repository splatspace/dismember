from dismember.models.user import User
from dismember.service import db
from dismember.user import user_bp
from dismember.wtforms_components.fields import remove_empty_password_fields
from dismember.wtforms_components.forms import DismemberModelForm
from flask import render_template, request, flash, redirect, url_for

from flask.ext.login import login_required, current_user
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, EqualTo
from wtforms_components import EmailField, Unique, read_only, PhoneNumberField


class MyDetailsForm(DismemberModelForm):
    email = EmailField(label='E-mail Address', validators=[
        DataRequired(),
        Unique(User.email, message='That e-mail address is assigned to another user')
    ])

    password_field = lambda required=False: PasswordField(validators=[
        Optional(),
        EqualTo('password_confirm', message='Passwords must match')
    ])
    password_confirm_field = lambda: PasswordField('Password (again)')

    full_name = StringField(label='Full Name', validators=[
        DataRequired(),
    ])

    address = StringField(label='Address', validators=[
        DataRequired(),
    ])

    phone = StringField(label='Phone Number', validators=[
        DataRequired(),
    ])

    emergency_contact = StringField(label='Emergency Contact', validators=[
        DataRequired(),
    ])

    update = SubmitField('Update')

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(MyDetailsForm, self).__init__(formdata, obj, prefix, **kwargs)
        read_only(self.email)


@user_bp.route('/me', methods=['GET'])
@login_required
def me():
    form = MyDetailsForm(obj=current_user)
    return render_template('/user/me.html',
                           form=form)


@user_bp.route('/me', methods=['POST'])
@login_required
def me_update():
    user = current_user
    form = MyDetailsForm(request.form, obj=user)
    if form.validate():
        remove_empty_password_fields(form)
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash('Your user details have been updated.')
        return redirect(url_for('.me', user_id=user.id))
    return render_template('/user/me.html',
                           form=form,
                           user=user)
