from django.db import models

# Create your models here.
from users.models import Businessman, Customer
from django.conf import settings



max_english_chars = settings.SMS_PANEL['ENGLISH_MAX_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']

class SMSTemplate(models.Model):

    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=160)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)


    def __str__(self):
        return self.title


class SentSMS(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    message_id = models.IntegerField()
    receptor = models.CharField(max_length=15, null=True)


class UnsentPlainSMS(models.Model):

    message = models.CharField(max_length=max_english_chars)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    customers = models.ManyToManyField(Customer)

class UnsentTemplateSMS(models.Model):

    template = models.CharField(max_length=template_max_chars)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    customers = models.ManyToManyField(Customer)

class SMSMessage(models.Model):


    PLAIN = '0'
    TEMPLATE = '1'
    CANCLE = '0'
    PENDING = '1'
    DONE = '2'
    FAILED = '3'

    message_type_choices = [
        (PLAIN, 'PLAIN'),
        (TEMPLATE, 'TEMPLATE')
    ]

    message_send_status = [
        (CANCLE, 'CANCLE'),
        (PENDING, 'PENDING'),
        (DONE, 'DONE'),
        (FAILED, 'FAILED')
    ]

    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    receptors = models.ManyToManyField(Customer, related_name='receptors')
    message = models.CharField(max_length=800)
    message_type = models.CharField(max_length=2, choices=message_type_choices)
    send_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=message_send_status, default='1')
