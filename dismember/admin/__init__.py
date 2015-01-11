from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, template_folder='templates')

import users
import roles
import member_types


def admin_index():
    return render_template('admin/index.html', sections=[
        ('admin.users_list', 'Users'),
        ('admin.roles_list', 'Roles'),
        ('admin.member_types_list', 'Member Types')
    ])


admin_bp.add_url_rule('/', endpoint='index', view_func=admin_index, strict_slashes=False)
