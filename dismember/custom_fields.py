from peewee import PostgresqlDatabase, DateTimeField


class DateTimeWithTimeZoneField(DateTimeField):
    """
    A custom timestamp with time zone.

    PostgresqlExtDatabase has one of these (DateTimeTZField), but that module requires
    installing HStore extensions in the database.  This approach does not require that.
    """
    db_field = 'datetime_tz'


def register_postgresql_fields():
    """
    Register custom fields used by models in this package and subpackages on a
    PostgresqlDatabase object.  Fields must be registered before the Flask-peewee
    Database wrapper class is constructed.
    """
    PostgresqlDatabase.register_fields({
        'datetime_tz': 'timestamp with time zone',
    })

