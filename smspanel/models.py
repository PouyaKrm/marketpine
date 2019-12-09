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
    resend_start = models.PositiveIntegerField()
    resend_stop = models.PositiveIntegerField(default=0)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

class UnsentTemplateSMS(models.Model):

    template = models.CharField(max_length=template_max_chars)
    resend_start = models.PositiveIntegerField()
    resend_stop = models.PositiveIntegerField(default=0)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
