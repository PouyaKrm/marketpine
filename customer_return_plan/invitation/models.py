from django.db import models
from django.conf import settings
# Create your models here.
from customer_return_plan.models import BaseInvitationDiscountSettings, Discount
from smspanel.models import SMSMessage
from users.models import Customer, Businessman, BusinessmanManyToOneBaseModel


class FriendInvitation(BusinessmanManyToOneBaseModel):

    TYPE_INVITED = '0'
    TYPE_INVITER = '1'
    invitation_type_choices = [
        (TYPE_INVITED, 'Invited'),
        (TYPE_INVITER, 'inviter')
    ]

    customer = models.OneToOneField(Customer, related_name='customer', null=True, on_delete=models.SET_NULL)
    invitation_type = models.CharField(max_length=2, choices=invitation_type_choices, null=True)
    new = models.BooleanField(default=True)
    discount = models.OneToOneField(Discount, on_delete=models.PROTECT, null=True)
    sms_message = models.OneToOneField(SMSMessage, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'friend_invitation'

    def __str__(self):
        return f'{self.id} - {self.businessman.username}'


class FriendInvitationSettings(BaseInvitationDiscountSettings):

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    sms_template = models.CharField(max_length=600, null=True)
    disabled = models.BooleanField(default=False)
