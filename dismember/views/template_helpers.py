from dismember.service import app

_currency_formats = {
    'USD': '$%s'
}


def format_currency(iso_4217_currency_code, amount):
    """Format the specified amount as the specified currency."""
    return _currency_formats.get(iso_4217_currency_code, '?%s') % amount


@app.context_processor
def inject_template_helpers():
    """Inject some helper functions for template rendering."""
    return dict(format_currency=format_currency)