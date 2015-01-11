from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, template_folder='templates')

import users
import roles
import member_types
import prox_credentials


def admin_index():
    modules = (
        users,
        roles,
        member_types,
        prox_credentials,
    )
    sections = [(m.crud_view.endpoints['list_endpoint'], m.crud_view.item_type_plural) for m in modules]

    return render_template('admin/index.html', sections=sections)


admin_bp.add_url_rule('/', endpoint='index', view_func=admin_index, strict_slashes=False)
