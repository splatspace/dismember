import datetime

from dismember.service import db


class Payment(db.Model):
    """
    Money given to the organization, possibly in exchange for goods or services.  This class is
    intended to be subclassed for different types of payments (dues, donations, etc.).
    """

    # class Meta:
    # db_table = 'subclasses_must_define_the_table_name'

    id = PrimaryKeyField()
    currency = Column(Text, nullable=False)
    amount = DecimalField(max_digits=11, decimal_places=2)
    created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return '%s' % self.currency.format(self.amount)