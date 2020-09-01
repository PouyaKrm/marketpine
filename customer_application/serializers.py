from django.db.models import QuerySet
from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj
from common.util.custom_validators import phone_validator
from customer_application.services import customer_data_service
from customer_return_plan.invitation.services import invitation_service
from customers.services import customer_service
from mobile_app_conf.models import MobileAppPageConf, MobileAppHeader
from mobile_app_conf.serializers import MobileAppPageConfSerializer, FileFieldWithLinkRepresentation
from mobile_app_conf.services import mobile_page_conf_service
from users.models import Businessman


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


class CustomerLoginSerializer(CustomerPhoneSerializer):
    code = serializers.CharField(max_length=300)

    class Meta:
        fields = [
            'phone',
            'code'
        ]


class BaseBusinessmanSerializer(BaseModelSerializerWithRequestObj):
    date_joined = serializers.SerializerMethodField(read_only=True)
    customers_total = serializers.SerializerMethodField(read_only=True)
    invitation_discount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'id',
            'business_name',
            'date_joined',
            'logo',
            'customers_total',
            'invitation_discount'
        ]

    def get_date_joined(self, obj: Businessman):
        return customer_service.get_date_joined(self.request.user, obj)

    def get_customers_total(self, obj: Businessman):
        return obj.customers.count()

    def get_invitation_discount(self, obj: Businessman):
        setting = invitation_service.get_businessman_invitation_setting_or_create(obj)
        return {'disabled': setting.disabled, 'percent_off': setting.percent_off,
                'flat_rate_off': setting.flat_rate_off, 'discount_type': setting.discount_type}



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

    class Meta:
        model = MobileAppPageConf
        fields = [
            'description',
            'is_location_set',
            'location_lat',
            'location_lng',
            'headers',
        ]


class BusinessmanRetrieveSerializer(BaseBusinessmanSerializer):
    page_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'id',
            'business_name',
            'date_joined',
            'logo',
            'customers_total',
            'invitation_discount',
            'page_data',
        ]

    def get_page_data(self, obj: Businessman):
        p = mobile_page_conf_service.get_businessman_conf_or_create(obj)
        return BusinessmanPageDataSerializer(p, context={'request': self.request}).data
