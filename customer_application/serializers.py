from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj
from common.util.custom_validators import phone_validator
from customers.services import customer_service
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


class BusinessmanListSerializer(BaseModelSerializerWithRequestObj):

    date_joined = serializers.SerializerMethodField(read_only=True)
    customers_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'business_name',
            'date_joined',
            'logo',
            'customers_total'
        ]

    def get_date_joined(self, obj: Businessman):
        return customer_service.get_date_joined(self.request.user, obj)

    def get_customers_total(self, obj: Businessman):
        return obj.customers.count()