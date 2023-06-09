import os

from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models

from common.util import generate_url_safe_base64_file_name
from common.util.custom_validators import pdf_file_validator

# Create your models here.
from common.util.sms_panel.client import ClientManagement, sms_client_management
from smspanel.models import SMSMessage
from users.models import Businessman, AuthStatus
from django.conf import settings
from base_app.models import PrivateFileStorage, PublicFileStorage

max_message_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']
min_credit = settings.SMS_PANEL['MIN_CREDIT']

auth_fs = PrivateFileStorage('auth-docs/', '/auth-docs/')


class SMSPanelStatus:
    ACTIVE_LOGIN = '1'
    ACTIVE = '2'
    INACTIVE = '0'


class SMSPanelInfo(models.Model):

    STATUS_INACTIVE = 'Disabled'
    STATUS_ACTIVE_LOGIN = 'Approved'
    STATUS_ACTIVE = 'ApprovedWithoutLogin'

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    api_key = models.TextField(default=None, null=True)
    STATUS_CHOICES = [(STATUS_ACTIVE_LOGIN, 'ACTIVE_LOGIN'), (STATUS_INACTIVE, 'INACTIVE'), (STATUS_ACTIVE, 'ACTIVE')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='0')
    minimum_allowed_credit = models.PositiveIntegerField(default=10000)
    credit = models.PositiveIntegerField(default=1000)
    sms_farsi_cost = models.PositiveSmallIntegerField()
    sms_english_cost = models.PositiveIntegerField()

    def deactivate(self):

        """
        deactivates sms panel of the user in kavenegar
        :return:
        """

        ClientManagement().deactivate_sms_panel(self.api_key)
        self.status = SMSPanelStatus.INACTIVE
        self.save()

    def activate(self):

        """
        activates sms panel on kavenegar
        :return:
        """

        if self.status == SMSPanelStatus.ACTIVE_LOGIN:
            return

        sms_client_management.activate_sms_panel(self.api_key)
        self.status = SMSPanelStatus.ACTIVE_LOGIN
        self.businessman.has_sms_panel = True
        self.businessman.save()
        self.save()

    def create_sms_panel(self, user: Businessman, password: str):
        info = sms_client_management.add_user(user, password)
        info.businessman = user
        info.save()
        return info
        
    def update_panel_info(self):
        info = sms_client_management.fetch_user(self.businessman)
        self.api_key = info.api_key
        self.credit = info.credit
        self.sms_farsi_cost = info.sms_farsi_cost
        self.sms_english_cost = info.sms_english_cost
            
        self.save()

    def refresh_credit(self):
        self.credit = sms_client_management.fetch_credit(self.api_key)
        self.save()

    def remained_credit_for_new_message(self):
        reserved_credit = 0
        for m in self.businessman.smsmessage_set.filter(status=SMSMessage.STATUS_PENDING).all():
            reserved_credit += m.reserved_credit
        return self.credit - reserved_credit

    def has_min_credit(self) -> bool:
        return self.credit >= min_credit

    def has_remained_credit_for_new_message_to_all(self):
        return self.remained_credit_for_new_message() > max_message_cost * self.businessman.customers.count()

    def has_valid_credit_to_send_message_to_all(self) -> bool:
        return self.has_min_credit() and self.has_remained_credit_for_new_message_to_all()

    def reduce_credit_local(self, costs):
        self.credit -= costs
        self.save()

    @staticmethod
    def get_businessman_api_key(user: Businessman) -> str:
        result = SMSPanelInfo.objects.filter(businessman=user).first()
        if result is None:
            return None
        return result.api_key

    def credit_in_tomans(self) -> int:
        return self.credit / 10

    def is_status_active(self):
        return self.status == SMSPanelInfo.STATUS_ACTIVE

    def is_status_active_login(self):
        return self.status == SMSPanelInfo.STATUS_ACTIVE_LOGIN

    def is_status_disabled(self):
        return self.status == SMSPanelInfo.STATUS_INACTIVE

class BusinessmanAuthDocs(models.Model):

    """
    Model that holds authentication data that is needed to authorize user
    """

    def get_upload_path(self, filename):
        return f'{self.businessman.id}/{generate_url_safe_base64_file_name(filename)}'

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    form = models.FileField(storage=auth_fs, upload_to=get_upload_path, max_length=300, null=True)
    national_card = models.ImageField(storage=auth_fs, upload_to=get_upload_path, max_length=300, null=True)
    birth_certificate = models.ImageField(storage=auth_fs, upload_to=get_upload_path, max_length=300, null=True)

    def __str__(self):
        return self.businessman.__str__()

    def businessman_username(self):
        return self.businessman.__str__()
