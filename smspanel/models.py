from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models

# Create your models here.
from django.db.models import QuerySet
from django.utils import timezone

from groups.models import BusinessmanGroups
from users.models import Businessman, Customer, BusinessmanManyToOneBaseModel, BusinessmanOneToOneBaseModel, BaseModel
from django.conf import settings

page_size = settings.PAGINATION_PAGE_NUM

max_english_chars = settings.SMS_PANEL['ENGLISH_MAX_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
send_max_fail_attempts = settings.SMS_PANEL['MAX_SEND_FAIL_ATTEMPTS']
max_message_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']
api_key = settings.SMS_PANEL['API_KEY']


class SMSTemplate(models.Model):
    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=160)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


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
    USED_FOR_SEND_TO_ALL = '6'

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
        (USED_FOR_FRIEND_INVITATION, 'FRIEND INVITATION'),
        (USED_FOR_SEND_TO_ALL, 'SEND TO ALL')
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
    current_receiver_id = models.BigIntegerField(default=0)
    last_receiver_id = models.BigIntegerField(default=0)

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

    def is_message_type_plain(self) -> bool:
        return self.message_type == SMSMessage.TYPE_PLAIN

    def __str__(self):
        return '{} - {}'.format(self.id, self.businessman.username)


class SMSMessageReceiverGroup(BaseModel):
    sms_message = models.OneToOneField(
        SMSMessage,
        on_delete=models.CASCADE,
        related_name='related_receiver_group',
        related_query_name='related_receiver_group'
    )
    group = models.ForeignKey(
        BusinessmanGroups,
        on_delete=models.CASCADE,
        related_name='related_sms_message',
        related_query_name='related_sms_message'
    )


class SentSMS(BaseModel):
    sms_message = models.ForeignKey(SMSMessage, on_delete=models.PROTECT, null=True,
                                    related_name='sent_sms', related_query_name='sent_sms')
    message_id = models.CharField(max_length=100)
    message = models.TextField(null=True)
    receptor = models.CharField(max_length=20, null=True)
    status = models.IntegerField(null=True)
    status_text = models.TextField(null=True)
    sender = models.TextField(null=True)
    cost = models.IntegerField(null=True)
    date = models.BigIntegerField(null=True)

    @staticmethod
    def get_all_businessman_sent_messages(user: Businessman):
        return SentSMS.objects.filter(businessman=user).order_by('-create_date').all()

    @staticmethod
    def get_sent_sms_from_kavenegar(user: Businessman, page_num, receptor: str = None) -> (int, int, bool, bool, list):

        """
        retrieve sent messages for businessman from kavenegar
        Args:
            user: businessman
            page_num: number of page for pagination
            receptor: if not None filters SentSms by receptor
        Returns: (int: page number. this value always equal to page_num prameter,
        int: count,
        bool: hasNextPage,
        bool: hasPreviousPage, list: list of sent messages from kavenegar)

        """

        from common.util.sms_panel.message import retrive_sent_messages
        from panelprofile.models import SMSPanelInfo
        query = SentSMS.get_all_businessman_sent_messages(user)
        if receptor is not None:
            query = query.filter(receptor=receptor)
        p = Paginator(query, page_size)
        pn = page_num
        try:
            page = p.page(page_num)
        except (PageNotAnInteger, EmptyPage) as e:
            pn = 1
            page = p.page(pn)
        message_ids = [s.message_id for s in page.object_list]
        if len(message_ids) == 0:
            return pn, query.count(), page.has_next(), page.has_previous(), message_ids
        return pn, query.count(), page.has_next(), page.has_previous(), retrive_sent_messages(api_key, message_ids)


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


class SMSMessageReceivers(models.Model):
    sms_message = models.ForeignKey(SMSMessage, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    sent_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ['sms_message', 'customer']


class WelcomeMessage(BusinessmanOneToOneBaseModel):
    message = models.CharField(null=True, blank=True, max_length=max_english_chars)
    send_message = models.BooleanField(default=False)
