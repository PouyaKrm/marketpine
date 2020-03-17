from django.db import models
from django.utils import timezone

from users.models import Businessman, Customer
from smspanel.models import SMSMessage


# Create your models here.


class Festival(models.Model):

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_code = models.CharField(max_length=12)
    sms_message = models.OneToOneField(SMSMessage, on_delete=models.CASCADE, null=True)  # max length of of one sms message is 70 characters
    message_sent = models.BooleanField(default=False)
    percent_off = models.FloatField(default=0)
    flat_rate_off = models.PositiveIntegerField(default=0)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer)

    class Meta:

        unique_together = [['businessman', 'name'], ['businessman', 'discount_code']]

    def is_expired(self) -> bool:
        return self.end_date < timezone.now().date()

    def can_edit(self) -> bool:
        return (not self.is_expired()) and (not self.message_sent)

    def can_delete(self) -> bool:
        return self.is_expired() or (not self.message_sent)
# class CustomerFestival(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     festival = models.ForeignKey(Festival, on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = ['customer', 'festival']
