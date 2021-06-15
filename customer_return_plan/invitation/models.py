from django.db import models
# Create your models here.
from django.db.models.aggregates import Sum

from customer_return_plan.models import BaseDiscountSettings, Discount
from smspanel.models import SMSMessage
from users.models import Customer, Businessman, BusinessmanManyToOneBaseModel, BusinessmanCustomer


class FriendInvitation(BusinessmanManyToOneBaseModel):
    inviter = models.ForeignKey(BusinessmanCustomer, related_name='inviter', null=True, on_delete=models.SET_NULL)
    invited = models.ForeignKey(BusinessmanCustomer, related_name='invited', null=True, on_delete=models.SET_NULL)
    new = models.BooleanField(default=True)
    inviter_discount = models.OneToOneField(Discount, related_name='inviter_discount', on_delete=models.PROTECT,
                                            null=True)
    invited_discount = models.OneToOneField(Discount, related_name='invited_discount', on_delete=models.PROTECT,
                                            null=True)
    sms_message = models.OneToOneField(SMSMessage, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'friend_invitation'
        unique_together = [['businessman', 'invited']]

    def __str__(self):
        return f'{self.id} - {self.businessman.username}'

    @staticmethod
    def customer_total_invitations_count(customer: Customer) -> int:
        return FriendInvitation.objects.filter(inviter=customer).count()

    @staticmethod
    def customer_all_invited_friend_purchases_sum(user: Businessman, inviter: Customer) -> int:
        result = FriendInvitation.objects.filter(businessman=user, inviter=inviter)\
            .aggregate(Sum('invited__purchases__amount')).get('invited__purchases__amount__sum')
        if result is None:
            return 0
        return result


class FriendInvitationSettings(BaseDiscountSettings):

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    sms_template = models.CharField(max_length=600, null=True)
    disabled = models.BooleanField(default=False)
