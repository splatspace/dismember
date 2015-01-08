from string import capitalize

from dismember.admin import admin_bp
from dismember.admin.crud_view import configure_crud_view
from dismember.models.user import User
from dismember.service import db
from dismember.wtforms_alchemy.forms import SessionModelForm, TimeZoneAwareFieldMeta
from flask import url_for, request, redirect, render_template, flash


class UserForm(SessionModelForm):
    class Meta(TimeZoneAwareFieldMeta):
        model = User


class NewUserForm(UserForm):
    class Meta(UserForm.Meta):
        exclude = ['confirmed_at', 'last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip',
                   'login_count']

users_view = configure_crud_view(admin_bp, 'users', User, NewUserForm, UserForm, 'user', 'users', User.full_name)
