from flask import render_template

from dismember.service import app
from flask.ext.login import login_required
from flask.ext.security import roles_required


@app.route('/board')
@login_required
@roles_required('board')
def board_index():
    return render_template('/board/index.html')