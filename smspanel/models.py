from django.db import models

# Create your models here.
from users.models import Businessman, Customer


class SMSTemplate(models.Model):

    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=200)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)


    def __str__(self):
        return self.title


class SentSMS(models.Model):
    content = models.CharField(max_length=150)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    sent_date = models.DateTimeField(auto_now_add=True)
    customers = models.ManyToManyField(Customer)


# class CustomerSentSMS(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     sms = models.ForeignKey(SentSMS, on_delete=models.CASCADE)
#     sent_date = models.DateTimeField(auto_now_add=True)
#
#
# SentSMS.customer = models.ManyToManyField(Customer, through=CustomerSentSMS)