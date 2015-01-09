from wtforms.widgets import html_params, HTMLString


class BootstrapCheckboxSelectGroup(object):
    def __init__(self):
        super(BootstrapCheckboxSelectGroup, self).__init__()

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('_class', 'checkbox')
        html = ['<div %s>' % html_params(**kwargs)]
        for subfield in field:
            html.append('<div class="checkbox">')
            html.append('%s %s' % (subfield(), subfield.label))
            html.append('</div>')
        html.append('</div>')
        return HTMLString(''.join(html))

class BootstrapCheckboxInput(object):
    def __init__(self):
        super(BootstrapCheckboxInput, self).__init__()

def __call__(self, field, **kwargs):
    kwargs.setdefault('id', field.id)
    kwargs.setdefault('_class', 'checkbox')
    html = ['<div %s>' % html_params(**kwargs)]
    for subfield in field:
        html.append('<div class="checkbox">')
        html.append('%s %s' % (subfield(), subfield.label))
        html.append('</div>')
    html.append('</div>')
    return HTMLString(''.join(html))
