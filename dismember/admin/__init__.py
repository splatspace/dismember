from dismember.admin.users import UserView
from dismember.models.user import User
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates')

users_view = UserView.as_view('users')
admin_bp.add_url_rule('/users/', view_func=users_view, methods=['GET', 'POST'])
admin_bp.add_url_rule('/users/<obj_id>', view_func=users_view, methods=['GET', 'POST'])