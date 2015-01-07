from dismember.models.user import User
from dismember.service import app, db
from dismember.views.newadmin.model_form import DismemberModelForm
from flask import render_template
from wtforms_alchemy import model_form_factory


class UserForm(DismemberModelForm):
    class Meta:
        model = User

@app.route('/newadmin/users', methods=('GET', 'POST'))
def submit():
    form = UserForm()
    return render_template('/newadmin/users.html', form=form)