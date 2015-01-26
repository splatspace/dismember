from flask import Blueprint, render_template
from flask.ext.security import roles_accepted

admin_bp = Blueprint('admin', __name__, template_folder='templates')

import views.users
import views.roles
import views.member_types
import views.prox_credentials

admin_views = [
    (views.users.crud_view, 'glyphicon-user'),
    (views.roles.crud_view, 'glyphicon-certificate'),
    (views.member_types.crud_view, 'glyphicon-tags'),
    (views.prox_credentials.crud_view, 'glyphicon-lock')
]
"""View classes and recommended icons"""
