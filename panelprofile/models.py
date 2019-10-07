from django.db import models

# Create your models here.
from users.models import Businessman


class SMSPanelInfo(models.Model):

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    username = models.CharField(max_length=20)
    api_key = models.TextField()
    STATUS_CHOICES = [('1', 'ACTIVE_LOGIN'), ('0', 'INACTIVE'), ('2', 'ACTIVE')]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    minimum_allowed_credit = models.PositiveIntegerField(default=10000)
    credit = models.PositiveIntegerField(default=1000)
    sms_farsi_cost = models.PositiveSmallIntegerField()
    sms_english_cost = models.PositiveIntegerField()
