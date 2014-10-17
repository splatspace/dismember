from sqlalchemy import Column, Numeric


def money_column(nullable=False, **kwargs):
    # 10 total digits, 2 digits to the right of the decimal point, lets us hold
    # up to 99,999,999.99.
    return Column(Numeric(precision=10, scale=2), nullable=nullable, **kwargs)


_currency_formats = {
    'USD': '$%s'
}


def format_currency(iso_4217_currency_code, amount):
    """Format the specified amount as the specified currency."""
    return _currency_formats.get(iso_4217_currency_code, '?%s') % amount

