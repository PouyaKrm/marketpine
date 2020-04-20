from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
from django.utils import timezone

from users.models import Businessman, Customer
from django.conf import settings



max_english_chars = settings.SMS_PANEL['ENGLISH_MAX_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
send_max_fail_attempts = settings.SMS_PANEL['MAX_SEND_FAIL_ATTEMPTS']
max_message_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']

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
    message_id = models.CharField(max_length=100)
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

    TYPE_PLAIN = '0'
    TYPE_TEMPLATE = '1'
    STATUS_CANCLE = '0'
    STATUS_PENDING = '1'
    STATUS_DONE = '2'
    STATUS_FAILED = '3'
    STATUS_WAIT_FOR_CREDIT_RECHARGE = '4'
    USED_FOR_NONE = '0'
    USED_FOR_FESTIVAL = '1'
    USED_FOR_CONTENT_MARKETING = '2'
    USED_FOR_INSTAGRAM_MARKETING = '3'
    USED_FOR_WELCOME_MESSAGE = '4'
    USED_FOR_FRIEND_INVITATION = '5'

    message_type_choices = [
        (TYPE_PLAIN, 'PLAIN'),
        (TYPE_TEMPLATE, 'TEMPLATE')
    ]

    message_send_status = [
        (STATUS_CANCLE, 'CANCLE'),
        (STATUS_PENDING, 'PENDING'),
        (STATUS_DONE, 'DONE'),
        (STATUS_FAILED, 'FAILED'),
        (STATUS_WAIT_FOR_CREDIT_RECHARGE, 'Waiting for credit recharge')
    ]

    message_used_for_choices = [
        (USED_FOR_NONE, 'NONE'),
        (USED_FOR_FESTIVAL, 'FESTIVAL'),
        (USED_FOR_CONTENT_MARKETING, 'CONTENT MARKETING'),
        (USED_FOR_INSTAGRAM_MARKETING, 'INSTAGRAM MARKETING'),
        (USED_FOR_WELCOME_MESSAGE, 'WELCOME MESSAGE'),
        (USED_FOR_FRIEND_INVITATION, 'FRIEND INVITATION')
    ]

    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)
    receivers = models.ManyToManyField(Customer, related_name='receivers', through='SMSMessageReceivers')
    message = models.CharField(max_length=800)
    reserved_credit = models.PositiveIntegerField(default=0)
    send_fail_attempts = models.IntegerField(default=0)
    message_type = models.CharField(max_length=2, choices=message_type_choices)
    send_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=message_send_status, default='1')
    used_for = models.CharField(max_length=2, choices=message_used_for_choices, default='0')

    def set_done(self):
        self.status = SMSMessage.STATUS_DONE
        self.sent_date = timezone.now()
        self.save()

    def increase_send_fail_and_set_failed(self):
        self.send_fail_attempts = self.send_fail_attempts + 1
        if self.send_fail_attempts >= send_max_fail_attempts:
            self.status = SMSMessage.STATUS_FAILED
        self.save()

    def just_increase_fail_count(self):
        self.send_fail_attempts += 1
        self.save()

    def reset_to_pending(self):
        self.send_fail_attempts = 0
        self.status = SMSMessage.STATUS_PENDING
        self.save()

    def set_reserved_credit_by_receivers(self):
        self.reserved_credit = self.receivers.count() * max_message_cost
        self.save()

    def has_any_unsent_receivers(self):
        return SMSMessageReceivers.objects.filter(sms_message=self, is_sent=False).exists()

    def set_status_wait_charge(self):
        self.status = SMSMessage.STATUS_WAIT_FOR_CREDIT_RECHARGE
        self.save()

    def set_fail(self):
        self.status = SMSMessage.STATUS_FAILED
        self.save()


class SMSMessageReceivers(models.Model):

    sms_message = models.ForeignKey(SMSMessage, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    sent_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ['sms_message', 'customer']
