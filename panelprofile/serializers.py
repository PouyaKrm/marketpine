import os

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework.request import Request
from rest_framework.reverse import reverse
from rest_framework import serializers

from base_app.serializers import FileFieldWithLinkRepresentation
from common.util.kavenegar_local import APIException
from common.util.sms_panel.message import system_sms_message
from customers.services import customer_service
from payment.models import Payment
from users.models import AuthStatus, Businessman, BusinessCategory
from users.serializers import CategorySerializer
from users.services import businessman_service
from .models import SMSPanelInfo, BusinessmanAuthDocs
from django.conf import settings
from common.util.custom_validators import pdf_file_validator, validate_logo_size
from common.util.sms_panel.client import ClientManagement


class SMSPanelInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSPanelInfo
        fields = [
            'credit',
            'sms_farsi_cost',
            'status'
        ]


class BusinessmanProfileSerializer(serializers.ModelSerializer):

    auth_documents = serializers.SerializerMethodField(read_only=True)
    sms_panel_details = serializers.SerializerMethodField(read_only=True)
    business_category = CategorySerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(write_only=True, queryset=BusinessCategory.objects.all())
    defined_groups = serializers.SerializerMethodField(read_only=True)
    logo = FileFieldWithLinkRepresentation(read_only=True)

    customers_total = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = Businessman
        fields = [
            'id',
            'username',
            'is_page_id_set',
            'first_name',
            'last_name',
            'phone',
            'email',
            'logo',
            'business_category',
            'business_name',
            'date_joined',
            'authorized',
            'has_sms_panel',
            'panel_activation_date',
            'panel_expiration_date',
            'can_activate_panel',
            'duration_type',
            'auth_documents',
            'sms_panel_details',
            'category',
            'defined_groups',
            'customers_total'
        ]

        extra_kwargs = {'username': {'read_only': True}, 'phone': {'read_only': True},
                        'email': {'read_only': True},
                        'authorized': {'read_only': True},
                        'date_joined': {'read_only': True},
                        'is_page_id_set': {'read_only': True},
                        'panel_activation_date': {'read_only': True},
                        'panel_expiration_date': {'read_only': True}
                        }

    def generate_link(self, path: str):
        request = self.context['request']
        domain = request.META['HTTP_HOST']
        return 'http://' + domain + path

    def get_auth_documents(self, obj: Businessman):

        """
        gives the path of views in profiledownload app for downloading uploaded
        documents
        :param obj: configured Businessman
        :return: dictionary that it's values are retrieved urls of the views
        """

        commitment_form_link = self.generate_link(reverse('commitment_form_download'))

        if obj.authorized == AuthStatus.UNAUTHORIZED:
            return {'commitment_form': commitment_form_link}

        form_link = self.generate_link(reverse('auth_docs_download', args=['form']))
        national_card_link = self.generate_link(reverse('auth_docs_download', args=['card']))
        birth_certificate_link = self.generate_link(reverse('auth_docs_download', args=['certificate']))

        return {'commitment_form': commitment_form_link, 'form': form_link,
                'national_card': national_card_link, 'birth_certificate': birth_certificate_link}


    def get_sms_panel_details(self, obj: Businessman):

        if not obj.has_sms_panel:
            return None

        serializer = SMSPanelInfoSerializer(obj.smspanelinfo)
        return serializer.data

    def get_defined_groups(self, obj: Businessman):
        from groups.models import BusinessmanGroups
        return BusinessmanGroups.defined_groups_num(obj)

    def get_customers_total(self, obj: Businessman):
        user = self.context['user']
        return customer_service.get_businessman_customers(user).count()

    def validate_email(self, value):

        user = self.context['user']

        users_num = Businessman.objects.all().exclude(id=user.id).filter(email=value).count()

        if users_num is not 0:
            raise serializers.ValidationError('this email address is already taken')

        return value

    def update(self, instance: Businessman, validated_data):

        for key, value in validated_data.items():

            setattr(instance, key, value)

        category = validated_data.get('category')
        if category is not None:
            instance.business_category = category

        instance.save()

        return instance


class UploadImageSerializer(serializers.ModelSerializer):

    logo = serializers.ImageField(max_length=254, validators=[validate_logo_size])

    class Meta:

        model = Businessman
        fields = ['logo']

    def update(self, instance: Businessman, validated_data):

        logo = validated_data['logo']

        instance.logo = logo
        instance.save()

        return instance


class AuthSerializer(serializers.ModelSerializer):

    password = serializers.CharField(min_length=8, max_length=16, required=True, write_only=True)

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

        if user.has_sms_panel:
            user.smspanelinfo.update_panel_info()
        else:
            sms = SMSPanelInfo()
            sms.create_sms_panel(user, password)

        BusinessmanAuthDocs.objects.create(businessman=user, **validated_data)

        user.authorized = AuthStatus.PENDING
        user.has_sms_panel = True

        user.save()

        try:
            system_sms_message.send_admin_authroize_docs_uploaded(user.username)
        except APIException:
            pass

        return {**validated_data, 'password': password}
