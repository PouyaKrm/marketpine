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


class FriendInvitationDiscount(models.Model):

    friend_invitation = models.ForeignKey(FriendInvitation, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=9)
    INVITATION_ROLE_CHOICES = [
        ('IR', 'Inviter'),
        ('ID', 'Invited')
    ]
    role = models.CharField(max_length=2, choices=INVITATION_ROLE_CHOICES)

    class Meta:
        db_table = 'friend_invitation_discount'
        unique_together = ['friend_invitation', 'customer']
