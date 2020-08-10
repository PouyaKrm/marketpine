from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj
from common.util.custom_validators import phone_validator
from customers.services import customer_service
from mobile_app_conf.models import MobileAppPageConf, MobileAppHeader
from mobile_app_conf.serializers import MobileAppPageConfSerializer, FileFieldWithLinkRepresentation
from mobile_app_conf.services import mobile_page_conf_service
from users.models import Businessman


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

    class Meta:
        model = Businessman
        fields = [
            'id',
            'business_name',
            'date_joined',
            'logo',
            'customers_total'
        ]

    def get_date_joined(self, obj: Businessman):
        return customer_service.get_date_joined(self.request.user, obj)

    def get_customers_total(self, obj: Businessman):
        return obj.customers.count()



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
            'page_data'
        ]

    def get_page_data(self, obj: Businessman):
        p =  mobile_page_conf_service.get_businessman_conf_or_create(obj)
        return BusinessmanPageDataSerializer(p, context={'request': self.request}).data
