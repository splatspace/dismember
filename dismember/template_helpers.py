from dismember.currency import format_currency
from dismember.service import app
from flask import get_flashed_messages


def iso_date(date):
    return date.strftime('%Y-%m-%d')


def get_flashed_messages_except(with_categories=False, category_exclude_filter=[]):
    all_messages = get_flashed_messages(with_categories=True)
    filtered_messages = filter(lambda (c, m): c not in category_exclude_filter, all_messages)
    if with_categories:
        return filtered_messages
    else:
        return [message for category, message in filtered_messages]


@app.context_processor
def inject_template_helpers():
    """Inject some helper functions for template rendering."""
    return dict(format_currency=format_currency,
                iso_date=iso_date,
                get_flashed_messages_except=get_flashed_messages_except)


def date_format(value, fmt='%Y-%m-%d'):
    return value.strftime(fmt)


def datetime_format(value, fmt='%Y-%m-%d %H:%M:%s'):
    return value.strftime(fmt)


app.jinja_env.filters['date'] = date_format
app.jinja_env.filters['datetime'] = datetime_format
