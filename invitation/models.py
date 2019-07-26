from django.db import models

# Create your models here.
from users.models import Customer, Businessman


class FriendInvitation(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    inviter = models.ForeignKey(Customer, related_name='invited_friends', null=True, on_delete=models.SET_NULL)
    invited = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    invitation_date = models.DateField(auto_now_add=True)
    new = models.BooleanField(default=True)

    class Meta:
        db_table = 'friend_invitation'
        unique_together = [['businessman', 'invited']]


    def __str__(self):
        return f'{self.id} - {self.businessman.username}'


class FriendInviterDiscount(models.Model):

    friend_invitation = models.OneToOneField(FriendInvitation, on_delete=models.CASCADE)
    inviter = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=9)

    class Meta:
        db_table = 'friend_inviter_discount'
        unique_together = ['inviter', 'friend_invitation']


class InvitedFriendDiscount(models.Model):

    friend_invitation = models.OneToOneField(FriendInvitation, on_delete=models.CASCADE)
    invited = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=9)

    class Meta:
        db_table = 'friend_invited_discount'
        unique_together = ['invited', 'friend_invitation']