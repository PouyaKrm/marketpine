from django.db.models import QuerySet
from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj
from common.util.custom_validators import phone_validator
from content_marketing.models import Post
from customer_application.services import customer_data_service
from customer_return_plan.festivals.models import Festival
from customer_return_plan.invitation.services import invitation_service
from customer_return_plan.loyalty.models import CustomerPoints, CustomerLoyaltySettings, CustomerLoyaltyDiscountSettings
from customer_return_plan.loyalty.serializers import CustomerPointsSerializer, LoyaltySettingsSerializer, \
    LoyaltyDiscountSettingsSerializer
from customer_return_plan.loyalty.services import LoyaltyService
from customers.services import customer_service
from mobile_app_conf.models import MobileAppPageConf, MobileAppHeader
from mobile_app_conf.serializers import FileFieldWithLinkRepresentation, \
    ContactInfoSerializer
from mobile_app_conf.services import mobile_page_conf_service
from online_menu.serializers import OnlineMenuSerializer
from users.models import Businessman, Customer

customer_full_name_field = serializers.CharField(max_length=40)


class BusinessmanIdRelatedField(serializers.RelatedField):

    def get_queryset(self) -> QuerySet:
        c = self.context['user']
        return customer_data_service.get_all_businessmans(c)

    def to_internal_value(self, data: int):
        if data is None or type(data) != int or data <= 0:
            raise serializers.ValidationError('invalid businessman Id')
        if not customer_data_service.is_customer_jouned_to_businessman(self.context['user'], data):
            raise serializers.ValidationError('customer is not joined to this businessman')
        return customer_data_service.get_businessman_of_customer_by_id(self.context['user'], data)


class CustomerPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, validators=[phone_validator])

    class Meta:
        fields = [
            'phone'
        ]


class CustomerCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=300)

    class Meta:
        fields = [
            'code'
        ]


class CustomerLoginSerializer(CustomerPhoneSerializer, CustomerCodeSerializer):

    class Meta:
        fields = [
            'phone',
            'code'
        ]


class CustomerProfileSerializer(BaseModelSerializerWithRequestObj):

    full_name = customer_full_name_field

    class Meta:
        model = Customer
        fields = [
            'full_name'
        ]


class BaseBusinessmanSerializer(BaseModelSerializerWithRequestObj):
    date_joined = serializers.SerializerMethodField(read_only=True)
    customers_total = serializers.SerializerMethodField(read_only=True)
    invitation_discount = serializers.SerializerMethodField(read_only=True)
    logo = FileFieldWithLinkRepresentation()
    is_member = serializers.SerializerMethodField(read_only=True)
    page_id = serializers.SerializerMethodField(read_only=True)
    is_page_id_set = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'id',
            'business_name',
            'is_page_id_set',
            'page_id',
            'date_joined',
            'is_member',
            'logo',
            'customers_total',
            'invitation_discount'
        ]

        extra_kwargs = {'logo': {'read_only': True}}

    def get_date_joined(self, obj: Businessman):
        user = self.request.user
        if user.is_anonymous:
            return None
        is_joined = customer_data_service.is_customer_jouned_to_businessman(user, obj.id)
        if not is_joined:
            return None

        return customer_service.get_date_joined(self.request.user, obj)

    def get_is_member(self, obj: Businessman):
        user = self.request.user
        return not user.is_anonymous and customer_data_service.is_customer_jouned_to_businessman(user, obj.id)

    def get_customers_total(self, obj: Businessman):
        return obj.customers.count()

    def get_invitation_discount(self, obj: Businessman):
        setting = invitation_service.get_businessman_invitation_setting_or_create(obj)
        return {'disabled': setting.disabled, 'percent_off': setting.percent_off,
                'flat_rate_off': setting.flat_rate_off, 'discount_type': setting.discount_type}

    def get_page_id(self, obj: Businessman):
        return mobile_page_conf_service.get_businessman_conf_or_create(obj).page_id

    def get_is_page_id_set(self, obj: Businessman):
        page_id = mobile_page_conf_service.get_businessman_conf_or_create(obj).page_id
        return page_id is not None and page_id != ""


class BusinessmanMobileAppHeaderSerializer(serializers.ModelSerializer):
    header_image = FileFieldWithLinkRepresentation()

    class Meta:
        model = MobileAppHeader
        fields = [
            'header_image',
            'show_order'
        ]


class BusinessmanPageDataSerializer(serializers.ModelSerializer):
    headers = BusinessmanMobileAppHeaderSerializer(many=True, read_only=True)
    contact_info = ContactInfoSerializer(many=True)

    class Meta:
        model = MobileAppPageConf
        fields = [
            'contact_info',
            'description',
            'address',
            'is_address_set',
            'is_location_set',
            'location_lat',
            'location_lng',
            'page_id',
            'instagram_page_url',
            'telegram_url',
            'show_working_time',
            'working_time_from',
            'working_time_to',
            'headers',
        ]


class CustomerAppPointsSerializer(CustomerPointsSerializer):
    class Meta:
        model = CustomerPoints
        exclude = [
            'businessman',
            'customer'
        ]


class CustomerAppLoyaltyDiscountSettingsSerializer(LoyaltyDiscountSettingsSerializer):
    class Meta:
        model = CustomerLoyaltyDiscountSettings
        fields = [
            'id',
            'point',
            'discount_type',
            'discount_code',
            'percent_off',
            'flat_rate_off'
        ]


class CustomerAppLoyaltySettingsSerializer(LoyaltySettingsSerializer):
    discount_settings = CustomerAppLoyaltyDiscountSettingsSerializer(many=True)

    class Meta:
        model = CustomerLoyaltySettings
        fields = [
            'is_active',
            'discount_settings'
        ]


class BusinessmanRetrieveSerializer(BaseBusinessmanSerializer):
    page_data = serializers.SerializerMethodField(read_only=True)
    menus = serializers.SerializerMethodField(read_only=True)
    customerloyaltysettings = CustomerAppLoyaltySettingsSerializer(read_only=True)
    points = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'id',
            'business_name',
            'is_page_id_set',
            'page_id',
            'date_joined',
            'is_member',
            'logo',
            'customers_total',
            'invitation_discount',
            'page_data',
            'menus',
            'customerloyaltysettings',
            'points',
        ]

    def get_page_data(self, obj: Businessman):
        p = mobile_page_conf_service.get_businessman_conf_or_create(obj)
        return BusinessmanPageDataSerializer(p, context={'request': self.request}).data

    def get_menus(self, obj: Businessman):
        menus = customer_data_service.get_online_menus_by_businessman_id(obj.id)
        sr = OnlineMenuSerializer(menus, context={'request': self.request}, many=True)
        return sr.data

    def get_points(self, obj: Businessman):
        points = LoyaltyService.get_instance().get_customer_points(obj, self.request.user)
        return CustomerAppPointsSerializer(points).data


class FestivalNotificationSerializer(BaseModelSerializerWithRequestObj):
    businessman = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'businessman'
        ]

    def get_businessman(self, f: Festival):
        if f:
            d = BaseBusinessmanSerializer(f.businessman, request=self.request).data
            return d
        return {}


class PostNotificationSerializer(BaseBusinessmanSerializer):

    businessman = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'businessman'
        ]

    def get_businessman(self, p: Post):
        if p:
            d = BaseBusinessmanSerializer(p.businessman, request=self.request).data
            return d
        return {}
