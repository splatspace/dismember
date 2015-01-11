from flask import Blueprint, render_template
from flask.ext.security import roles_accepted

admin_bp = Blueprint('admin', __name__, template_folder='templates')

import views.users
import views.roles
import views.member_types
import views.prox_credentials


@roles_accepted('admin')
def admin_index():
    crud_views = [
        views.users.crud_view,
        views.roles.crud_view,
        views.member_types.crud_view,
        views.prox_credentials.crud_view
    ]

    icons = {
        views.users.crud_view.name: 'glyphicon-user',
        views.roles.crud_view.name: 'glyphicon-certificate',
        views.member_types.crud_view.name: 'glyphicon-tags',
        views.prox_credentials.crud_view.name: 'glyphicon-lock',
    }

    return render_template('admin/index.html', crud_views=crud_views, icons=icons)


admin_bp.add_url_rule('/', endpoint='index', view_func=admin_index, strict_slashes=False)
