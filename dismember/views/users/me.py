from flask import render_template

from dismember.service import app

@app.route('/users/me')
#@auth.login_required
def users_me():
    return render_template('/users/me.html')
