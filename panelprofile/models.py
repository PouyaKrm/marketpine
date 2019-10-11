import os

from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models

from common.util.custom_validators import pdf_file_validator

# Create your models here.
from common.util.sms_panel import ClientManagement
from users.models import Businessman, AuthStatus
from django.conf import settings

fs = FileSystemStorage(location=settings.MEDIA_ROOT)
auth_fs = FileSystemStorage(location=settings.MEDIA_ROOT + 'auth-docs/')


class SMSPanelStatus:
    ACTIVE_LOGIN = '1'
    ACTIVE = '2'
    INACTIVE = '0'


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
        ClientManagement().activate_sms_panel(self.api_key)
        self.status = SMSPanelStatus.ACTIVE_LOGIN
        self.save()


class AuthDoc(models.Model):

    file = models.FileField(storage=fs, upload_to='auth-doc', validators=[pdf_file_validator])


class BusinessmanAuthDocs(models.Model):

    """
    Model that holds authentication data that is needed to authorize user
    """

    def get_upload_path(self, filename):
        return f'{self.businessman.id}/auth-docs/{filename}'

    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    form = models.FileField(upload_to=get_upload_path, max_length=40, null=True)
    national_card = models.ImageField(upload_to=get_upload_path, max_length=40, null=True)
    birth_certificate = models.ImageField(upload_to=get_upload_path, max_length=40, null=True)

    def __str__(self):
        return self.businessman.__str__()

    def businessman_username(self):
        return self.businessman.__str__()

    def un_authorize_user(self):

        """
        deactivates sms panel, deletes auth dcs and sets auth status of the user to un authorized
        :return:
        """

        if self.businessman.authorized != AuthStatus.AUTHORIZED:
            self.businessman.authorized = AuthStatus.UNAUTHORIZED
            self.businessman.save()
            BusinessmanAuthDocs.objects.filter(id=self.id).delete()
            return

        self.businessman.smspanelinfo.deactivate()

        self.businessman.authorized = AuthStatus.UNAUTHORIZED

        self.businessman.save()
        BusinessmanAuthDocs.objects.filter(id=self.id).delete()

    def authorize_user(self):

        """
        sets businessman auth status to authorized and activates sms panel
        :return:
        """

        if self.businessman.authorized != AuthStatus.PENDING:
            return

        self.businessman.smspanelinfo.activate()
        self.businessman.authorized = AuthStatus.AUTHORIZED
        self.businessman.save()

    def delete(self, using=..., keep_parents: bool = ...):

        """
        sets businessman auth status to unauthorized in database and kavenegar(if user was authorized before).
        :param using:
        :param keep_parents:
        :return:
        """

        self.un_authorize_user()
