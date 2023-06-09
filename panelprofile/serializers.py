from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import serializers

from base_app.serializers import FileFieldWithLinkRepresentation, BaseModelSerializerWithRequestObj, \
    BaseSerializerWithRequestObj, ImageFiledWithLinkRepresentation
from common.util.custom_validators import validate_logo_size, phone_validator
from customers.services import customer_service
from payment.serializers import WalletSerializer
from payment.services import wallet_billing_service
from users.models import Businessman, BusinessCategory
from users.serializers import CategorySerializer
from users.services import businessman_service
from .models import SMSPanelInfo, BusinessmanAuthDocs
from .services import sms_panel_info_service


class SMSPanelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSPanelInfo
        fields = [
            'credit',
            'sms_farsi_cost',
            'status'
        ]


class BusinessmanProfileSerializer(BaseModelSerializerWithRequestObj):
    sms_panel_details = serializers.SerializerMethodField(read_only=True)
    business_category = CategorySerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(write_only=True, required=False, queryset=BusinessCategory.objects.all())
    defined_groups = serializers.SerializerMethodField(read_only=True)
    logo = FileFieldWithLinkRepresentation(read_only=True)
    customers_total = serializers.SerializerMethodField(read_only=True)
    wallet = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = Businessman
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone',
            'email',
            'logo',
            'business_category',
            'business_name',
            'date_joined',
            'is_phone_verified',
            'viewed_intro',
            'authorized',
            'has_sms_panel',
            'panel_activation_date',
            'panel_expiration_date',
            'can_activate_panel',
            'duration_type',
            'sms_panel_details',
            'category',
            'defined_groups',
            'customers_total',
            'wallet',
        ]

        extra_kwargs = {'username': {'read_only': True},
                        'first_name': {'required': False},
                        'last_name': {'required': False},
                        'business_name': {'required': False},
                        'phone': {'read_only': True},
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

    def get_sms_panel_details(self, obj: Businessman):

        has_panel = sms_panel_info_service.has_sms_panel(obj)
        if not has_panel:
            return None
        panel = sms_panel_info_service.fetch_sms_panel_info(obj)
        serializer = SMSPanelInfoSerializer(panel)
        return serializer.data

    def get_defined_groups(self, obj: Businessman):
        from groups.models import BusinessmanGroups
        return BusinessmanGroups.defined_groups_num(obj)

    def get_customers_total(self, obj: Businessman):
        user = self.request.user
        return customer_service.get_businessman_customers(user).count()

    def get_wallet(self, user: Businessman):
        w = wallet_billing_service.get_businessman_wallet_or_create(user)
        sr = WalletSerializer(w)
        return sr.data

    def validate_email(self, value):

        user = self.request.user

        users_num = Businessman.objects.all().exclude(id=user.id).filter(email=value).count()

        if users_num is not 0:
            raise serializers.ValidationError('this email address is already taken')

        return value

    def validate_phone(self, value):

        user = self.request.user
        if user.is_phone_verified:
            return None

        is_unique = businessman_service.is_phone_unique_for_update(user, value)
        if not is_unique:
            raise serializers.ValidationError('شماره تلفن یکتا نیست')
        return value

    def update(self, instance: Businessman, validated_data):

        pass
        # for key, value in validated_data.items():
        #
        #     setattr(instance, key, value)
        #
        # category = validated_data.get('category')
        # if category is not None:
        #     instance.business_category = category
        #
        # instance.save()
        #
        # return instance


class UploadImageSerializer(BaseModelSerializerWithRequestObj):
    logo = ImageFiledWithLinkRepresentation(max_length=254, validators=[validate_logo_size])

    class Meta:
        model = Businessman
        fields = ['logo']

    def update(self, instance: Businessman, validated_data):
        logo = validated_data['logo']

        instance.logo = logo
        instance.save()

        return instance


class AuthSerializer(BaseModelSerializerWithRequestObj):
    password = serializers.CharField(min_length=8, max_length=16, required=True, write_only=True)
    form = serializers.ImageField(max_length=300, required=True, write_only=True)

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

        user = self.request.user

        if authenticate(username=user.username, password=value) is None:
            raise serializers.ValidationError('کلمه عبور نا معتبر')

        return value

    def validate_form(self, value):

        if value.size > settings.AUTH_DOC['MAX_FORM_SIZE']:
            raise ValidationError('اندازه فایل بیش از حد مجاز است')

        return value

    def validate_national_card(self, value):

        if value.size > settings.AUTH_DOC['MAX_CARD_SIZE']:
            raise ValidationError('اندازه فایل بش از حد مجاز است')

        return value

    def validate_birth_certificate(self, value):

        if value.size > settings.AUTH_DOC['MAX_CERTIFICATE_SIZE']:
            raise ValidationError('ندازه فایل بیش از حد مجاز است')

        return value


class PhoneChangeSerializer(BaseSerializerWithRequestObj):

    phone = serializers.CharField(max_length=20, validators=[phone_validator], required=False)

    def __init__(self, is_phone_required: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = is_phone_required

    class Meta:
        fields = '__all__'

    def validate_phone(self, value):
        is_unique = businessman_service.is_phone_unique_for_update(self.request.user, value)
        if not is_unique:
            raise serializers.ValidationError('شماره تلفن یکتا نیست')
        return value
