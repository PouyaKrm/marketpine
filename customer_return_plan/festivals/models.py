from django.db import models
from django.utils import timezone

from customer_return_plan.models import Discount
from users.models import Businessman, Customer, BusinessmanManyToOneBaseModel
from smspanel.models import SMSMessage


# Create your models here.


class Festival(BusinessmanManyToOneBaseModel):

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    sms_message = models.OneToOneField(SMSMessage, on_delete=models.CASCADE, null=True)  # max length of of one sms message is 70 characters
    message_sent = models.BooleanField(default=False)
    discount = models.OneToOneField(Discount, on_delete=models.PROTECT, null=True)
    marked_as_deleted_for_businessman = models.BooleanField(default=False)

    class Meta:

        unique_together = [['businessman', 'name']]

    def is_expired(self) -> bool:
        return self.end_date < timezone.now().date()

    def can_edit(self) -> bool:
        return (not self.is_expired()) and (not self.message_sent)

    def can_delete(self) -> bool:
        return self.is_expired() or (not self.message_sent)

    def has_any_one_used_festival(self) -> bool:
        return self.discount.connected_purchases.count() > 0

    def mark_as_deleted(self):
        self.marked_as_deleted_for_businessman = True
        self.save()
