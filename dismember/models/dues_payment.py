#from dismember.models.payment import Payment
from dismember.models.user import User


class DuesPayment(Payment):
    """A Payment for dues."""

    class Meta:
        db_table = 'dues_payments'

    user = ForeignKeyField(User)
    period_begin = DateField()
    period_end = DateField()

    def __str__(self):
        return '%s (%s: %s to %s)' % (
            super(DuesPayment, self).__str__(), self.user.username, self.period_begin, self.period_end)


class DuesPaymentAdmin(ModelAdmin):
    def get_display_name(self):
        return 'Dues Payments'

    def get_admin_name(self):
        return 'dues_payments'


DuesPayment.create_table(fail_silently=True)