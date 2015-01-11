from flask import Blueprint

user_bp = Blueprint('user', __name__, template_folder='templates')

import views.dues_history
import views.me
import views.wepay_common
import views.wepay_donation
import views.wepay_dues