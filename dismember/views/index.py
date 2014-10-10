from flask import render_template

from dismember.service import app, auth

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
