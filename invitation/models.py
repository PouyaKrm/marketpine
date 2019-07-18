from django.db import models

# Create your models here.
from users.models import Customer, Businessman


class FriendInvitation(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(Customer, on_delete=models.CASCADE)
    friend_phone = models.CharField(max_length=15)
    invitation_date = models.DateField(auto_now_add=True)
    discount_used = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    new = models.BooleanField(default=True)

    class Meta:
        db_table = 'friend_invitation'
        unique_together = ['businessman', 'friend_phone']
