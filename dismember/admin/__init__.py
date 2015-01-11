from flask import Blueprint, render_template
from flask.ext.security import roles_accepted

admin_bp = Blueprint('admin', __name__, template_folder='templates')

import views.users
import views.roles
import views.member_types
import views.prox_credentials


@roles_accepted('admin')
def admin_index():
    modules = (
        views.users,
        views.roles,
        views.member_types,
        views.prox_credentials,
    )
    sections = [(m.crud_view.endpoints['list_endpoint'], m.crud_view.item_type_plural) for m in modules]

    return render_template('admin/index.html', sections=sections)


admin_bp.add_url_rule('/', endpoint='index', view_func=admin_index, strict_slashes=False)
