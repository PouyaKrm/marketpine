from django.db import models
from django.conf import settings
# Create your models here.
from smspanel.models import SMSMessage
from users.models import Customer, Businessman


class BaseInvitationDiscountSettings(models.Model):
    DISCOUNT_TYPE_PERCENT = '0'
    DISCOUNT_TYPE_FLAT_RATE = '1'

    discount_type_choices = [
        (DISCOUNT_TYPE_PERCENT, 'Percent'),
        (DISCOUNT_TYPE_FLAT_RATE, 'Flat rate')
    ]
    discount_type = models.CharField(max_length=2, null=True, choices=discount_type_choices,
                                     default=DISCOUNT_TYPE_PERCENT)
    percent_off = models.FloatField(default=0)
    flat_rate_off = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class FriendInvitation(BaseInvitationDiscountSettings):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    inviter = models.ForeignKey(Customer, related_name='invited_friends', null=True, on_delete=models.SET_NULL)
    invited = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    invitation_date = models.DateField(auto_now_add=True)
    new = models.BooleanField(default=True)
    inviter_discount_code = models.CharField(max_length=20, null=True)
    invited_discount_code = models.CharField(max_length=20, null=True)
    sms_message = models.OneToOneField(SMSMessage, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'friend_invitation'
        unique_together = [['businessman', 'invited']]


    def __str__(self):
        return f'{self.id} - {self.businessman.username}'


class FriendInvitationSettings(BaseInvitationDiscountSettings):

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    sms_template = models.CharField(max_length=600, null=True)
    disabled = models.BooleanField(default=False)

    def is_percent_discount(self) -> bool:
        return self.discount_type == FriendInvitationSettings.DISCOUNT_TYPE_PERCENT


class FriendInvitationDiscount(BaseInvitationDiscountSettings):

    DISCOUNT_ROLE_INVITER = 'IR'
    DISCOUNT_ROLE_INVITED = 'ID'

    friend_invitation = models.ForeignKey(FriendInvitation, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=9)
    used = models.BooleanField(default=False)
    INVITATION_ROLE_CHOICES = [
        (DISCOUNT_ROLE_INVITER, 'Inviter'),
        (DISCOUNT_ROLE_INVITED, 'Invited')
    ]
    role = models.CharField(max_length=2, choices=INVITATION_ROLE_CHOICES)
    # percent_off = models.FloatField(default=0)
    # flat_rate_off = models.PositiveIntegerField(default=0)
    # discount_type = models.CharField(max_length=2, choices=FriendInvitationSettings.discount_type_choices,
    #                                  default=FriendInvitationSettings.DISCOUNT_TYPE_PERCENT)

    class Meta:
        db_table = 'friend_invitation_discount'
        unique_together = ['friend_invitation', 'customer']


