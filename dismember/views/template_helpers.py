from dismember.currency import format_currency
from dismember.service import app

@app.context_processor
def inject_template_helpers():
    """Inject some helper functions for template rendering."""
    return dict(format_currency=format_currency)