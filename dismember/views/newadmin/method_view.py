from flask import url_for, render_template
from flask.views import MethodView


class DismemberAdminView(MethodView):
    # default template that we will use to display a list
    # of all items in a model
    list_template = 'admin/list_view.html'

    def __init__(self, model, endpoint, list_template=None):
        self.model = model
        self.endpoint = endpoint
        self.path = url_for('.%s' % self.endpoint)
        self.list_template = list_template

    def get(self):
        obj = self.model.query.all()
        return render_template(DismemberAdminView.list_template, obj=obj, path=self.path)


view = DismemberAdminView.as_view('blog')

# now we just add the url rule
admin.add_url_rule('/blog/', view_func=view, methods=['GET', 'POST'])