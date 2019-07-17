from django.db import models

# Create your models here.
from users.models import Customer


class FriendInvitation(models.Model):

    invited_by = models.ForeignKey(Customer, on_delete=models.CASCADE)
    friend_phone = models.CharField(max_length=15)
    invitation_date = models.DateField()

    class Meta:
        db_table = 'friend_invitation'
        unique_together = ['invited_by', 'friend_phone']
