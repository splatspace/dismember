from flask.ext.wtf import Form


class DismemberModelForm(Form):
    """
    A re-implementation of WTForms-Components's ModelForm that derives from Flask-WTF's Form
    so we can have hidden_tag() when rendering fields.
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(
            self, formdata=formdata, obj=obj, prefix=prefix, **kwargs
        )
        self._obj = obj

