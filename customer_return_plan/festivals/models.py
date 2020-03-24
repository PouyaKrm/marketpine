from django.db import models
from django.utils import timezone

from customer_return_plan.models import Discount
from users.models import Businessman, Customer
from smspanel.models import SMSMessage


# Create your models here.


class Festival(models.Model):

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    # discount_code = models.CharField(max_length=12)
    sms_message = models.OneToOneField(SMSMessage, on_delete=models.CASCADE, null=True)  # max length of of one sms message is 70 characters
    message_sent = models.BooleanField(default=False)
    # percent_off = models.FloatField(default=0)
    # flat_rate_off = models.PositiveIntegerField(default=0)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    # customers = models.ManyToManyField(Customer)
    discount = models.OneToOneField(Discount, on_delete=models.PROTECT, null=True)

    class Meta:

        unique_together = [['businessman', 'name']]

    def is_expired(self) -> bool:
        return self.end_date < timezone.now().date()

    def can_edit(self) -> bool:
        return (not self.is_expired()) and (not self.message_sent)

    def can_delete(self) -> bool:
        return self.is_expired() or (not self.message_sent)
