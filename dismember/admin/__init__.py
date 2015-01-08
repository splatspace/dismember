from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates')

import users

# users_view = UserView.as_view('users')
# admin_bp.add_url_rule('/users/', view_func=users_view, methods=['GET', 'POST'])
# admin_bp.add_url_rule('/users/<user_id>', view_func=users_view, methods=['GET', 'POST'])