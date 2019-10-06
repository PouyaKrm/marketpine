from django.db import models

# Create your models here.
from users.models import Businessman, Customer
from django.conf import settings


class SMSPanelInfo(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    username = models.CharField(max_length=20)
    api_key = models.CharField(max_length=50)
    STATUS_CHOICES = [('1', 'ACTIVE_LOGIN'), ('0', 'INACTIVE'), ('2', 'ACTIVE')]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    plan_id = models.IntegerField


class SMSTemplate(models.Model):

    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=200)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)


    def __str__(self):
        return self.title


class SentSMS(models.Model):
    content = models.CharField(max_length=settings.SMS_EN_MAX)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    sent_date = models.DateTimeField(auto_now_add=True)
    customers = models.ManyToManyField(Customer)
    is_plain_sms = models.BooleanField(default=False)


# class CustomerSentSMS(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     sms = models.ForeignKey(SentSMS, on_delete=models.CASCADE)
#     sent_date = models.DateTimeField(auto_now_add=True)
#
#
# SentSMS.customer = models.ManyToManyField(Customer, through=CustomerSentSMS)
