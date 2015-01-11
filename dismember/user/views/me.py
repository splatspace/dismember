from dismember.user import user_bp
from flask import render_template

from dismember.service import app
from flask.ext.login import login_required


@user_bp.route('/me')
@login_required
def me():
    return render_template('/user/me.html')
