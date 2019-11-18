import os

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import AuthStatus, Businessman
from .models import SMSPanelInfo, BusinessmanAuthDocs
from django.conf import settings
from common.util.custom_validators import pdf_file_validator, validate_logo_size
from common.util.sms_panel import ClientManagement


class BusinessmanProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = Businessman
        fields = [
            'username',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'business_name',
            'authorized',
        ]

        extra_kwargs = {'username': {'read_only': True}, 'phone': {'read_only': True}, 'email': {'read_only': True},
                        'authorized': {'read_only': True}}

    def validate_email(self, value):

        user = self.context['user']

        users_num = Businessman.objects.all().exclude(id=user.id).filter(email=value).count()

        if users_num is not 0:
            raise serializers.ValidationError('this email address is already taken')

        return value

    def update(self, instance, validated_data):

        for key, value in validated_data.items():

            setattr(instance, key, value)

        instance.save()

        return instance


class UploadImageSerializer(serializers.ModelSerializer):

    logo = serializers.ImageField(max_length=254, validators=[validate_logo_size])

    class Meta:

        model = Businessman
        fields = ['logo']

    def update(self, instance: Businessman, validated_data):

        logo = validated_data['logo']

        user = self.context['user']

        path = os.path.join(settings.MEDIA_ROOT, user.id.__str__(), 'logo')

        if not os.path.exists(path):
            os.makedirs(path)
        else:
            user.logo.delete()

        instance.logo.save(logo.name, logo.file)

        return instance



class AuthSerializer(serializers.ModelSerializer):

    password = serializers.CharField(min_length=8, max_length=16, required=True)
    class Meta:

        model = BusinessmanAuthDocs
        fields = [
            'form',
            'national_card',
            'birth_certificate',
            'password'
        ]

        extra_kwargs = {'national_card': {'required': True}, 'birth_certificate': {'required': True},
                        'form': {'required': True}}

    def validate_password(self, value):

        user = self.context['user']

        if authenticate(username=user.username, password=value) is None:
            raise serializers.ValidationError('کلمه عبور نا معتبر')

        return value

    def validate_form(self, value):

        if value.size > settings.AUTH_DOC['MAX_FORM_SIZE']:
            raise ValidationError('اندازه فایل بیش از حد مجاز است')

        pdf_file_validator(value)

        return value

    def validate_national_card(self, value):

        if value.size > settings.AUTH_DOC['MAX_CARD_SIZE']:
            raise ValidationError('اندازه فایل بش از حد مجاز است')

        return value

    def validate_birth_certificate(self, value):

        if value.size > settings.AUTH_DOC['MAX_CERTIFICATE_SIZE']:
            raise ValidationError('ندازه فایل بیش از حد مجاز است')

        return value

    def create(self, validated_data: dict):

        user = self.context['user']

        password = validated_data.pop('password')

        client_manage = ClientManagement()


        if hasattr(user, 'smspanelinfo'):

            pass
            # info = client_manage.fetch_user(user)
            #
            # user_info = user.smspanelinfo
            #
            # user_info.api_key = info.api_key
            #
            # user_info.credit = info.credit
            # user_info.sms_farsi_cost = info.sms_farsi_cost
            # user_info.sms_english_cost = info.sms_english_cost
            #
            # user_info.save()



        else:
            pass
            # info = client_manage.add_user(user, password)
            # info.businessman = user
            # info.save()

        BusinessmanAuthDocs.objects.create(businessman=user, **validated_data)

        user.authorized = AuthStatus.PENDING

        user.save()

        return {**validated_data, 'password': password}
