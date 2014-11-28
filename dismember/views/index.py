from flask import render_template, flash

from dismember.service import app


@app.route('/')
def index():
    return render_template('index.html')
