from flask import render_template

from dismember.service import app
from flask.ext.login import login_required


@app.route('/users/me')
@login_required
def users_me():
    return render_template('/users/me.html')
