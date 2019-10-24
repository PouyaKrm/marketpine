from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import AuthStatus
from .models import SMSPanelInfo, BusinessmanAuthDocs
from django.conf import settings
from common.util.custom_validators import pdf_file_validator
from common.util.sms_panel import ClientManagement


class AuthAuthenticateUserSerializer(serializers.Serializer):

    password = serializers.CharField(min_length=8, max_length=16)


    def businessman(self, user):
        self.context['user'] = user

    def create(self, validated_data):

        """
        if user is sending documents for the first time, creates sms panle info for the user and a client on kavenegar
         and sets authorized to pending. If user has SMSPanelIfo record, fetches data from kavenegar and updates
        SMSPanelInfo of the user and sets authorized property of the user to PENDING.
        In both cases authentication is finished and user can not upload auth doc any more.
        :param validated_data:
        :return: password
        """

        user = self.context['user']

        password = validated_data.get('password')

        client_manage = ClientManagement()

        if hasattr(user, 'smspanelinfo'):

            info = client_manage.fetch_user(user)

            user_info = user.smspanelinfo

            user_info.api_key = info.api_key

            user_info.credit = info.credit
            user_info.sms_farsi_cost = info.sms_farsi_cost
            user_info.sms_english_cost = info.sms_english_cost

            user_info.save()

            user.authorized = AuthStatus.PENDING

            user.save()

            return password

        info = client_manage.add_user(user, password)
        info.businessman = user
        info.save()

        user.authorized = AuthStatus.PENDING

        user.save()

        password

def validate_form(file):

    if file.size > settings.AUTH_DOC['MAX_FORM_SIZE']:
        raise ValidationError('اندازه فایل بیش از حد مجاز است')

    return file



def validate_card(file):

    if file.size > settings.AUTH_DOC['MAX_CARD_SIZE']:
        raise ValidationError('اندازه فایل بش از حد مجاز است')

    return file

def validate_certificate(file):

    if file.size > settings.AUTH_DOC['MAX_CERTIFICATE_SIZE']:

        raise ValidationError('ندازه فایل بیش از حد مجاز است')

    return file

class AuthFormSerializer(serializers.ModelSerializer):

    form = serializers.FileField(max_length=40, validators=[pdf_file_validator, validate_form])
    class Meta:
        model = BusinessmanAuthDocs
        fields = [
            'form'
        ]


    def update(self, instance: BusinessmanAuthDocs, validated_data: dict):

        """
        deletes previous file form if exist and saves new one
        :param instance: BusinessmanAuthDocs
        :param validated_data: contains new form
        :return:
        """
        if instance.form.name is not None:
            instance.form.delete()
        # instance.form = validated_data.get('form')
        new_form = validated_data.get('form')
        instance.form.save(new_form.name, new_form.file)
        instance.form.close()
        return instance


class AuthNationalCardSerializer(serializers.ModelSerializer):

    national_card = serializers.ImageField(max_length=40, validators=[validate_card])
    class Meta:
        model = BusinessmanAuthDocs
        fields = [
            'national_card'
        ]

    def update(self, instance: BusinessmanAuthDocs, validated_data: dict):

        if instance.national_card.name is not None:
            instance.form.delete()

        instance.national_card = validated_data.get('national_card')
        instance.save()
        return instance


class AuthBirthCertificateSerializer(serializers.ModelSerializer):

    birth_certificate = serializers.ImageField(max_length=40, validators=[validate_certificate])

    class Meta:
        model = BusinessmanAuthDocs
        fields = [
            'birth_certificate'
        ]

    def update(self, instance: BusinessmanAuthDocs, validated_data):

        if instance.birth_certificate.name is not None:
            instance.delete()
        instance.birth_certificate = validated_data.get('birth_certificate')

        instance.save()

        return instance

class SMSPanelInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSPanelInfo
        read_only_fields = [
            'status',
            'minimum_allowed_credit',
            'credit'
        ]

