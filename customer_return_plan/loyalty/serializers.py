from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj
from customer_return_plan.serializers import WritableNestedDiscountSettingSerializer
from .models import CustomerLoyaltyDiscountSettings, CustomerPurchaseAmountDiscountSettings, \
    CustomerPurchaseNumberDiscountSettings, CustomerPoints, CustomerLoyaltySettings
from ..validation import validate_discount_value_by_discount_type


class PurchaseAmountSettingsSerializer(WritableNestedDiscountSettingSerializer):
    purchase_amount = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = CustomerPurchaseAmountDiscountSettings
        fields = WritableNestedDiscountSettingSerializer.Meta.fields + ['purchase_amount']

    def create(self, validated_data):
        pass


class PurchaseNumberSettingsSerializer(WritableNestedDiscountSettingSerializer):
    purchase_number = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = CustomerPurchaseNumberDiscountSettings
        fields = WritableNestedDiscountSettingSerializer.Meta.fields + ['purchase_number']

    def create(self, validated_data):
        pass


class LoyaltyDiscountSettingsSerializer(BaseModelSerializerWithRequestObj):
    point = serializers.IntegerField(min_value=1, required=True)
    percent_off = serializers.IntegerField(min_value=0, max_value=100, required=True)
    flat_rate_off = serializers.IntegerField(min_value=0, required=True)
    discount_type = serializers.ChoiceField(choices=CustomerLoyaltyDiscountSettings.discount_type_choices)

    class Meta:
        model = CustomerLoyaltyDiscountSettings
        fields = [
            'point',
            'discount_code',
            'discount_type',
            'percent_off',
            'flat_rate_off',
        ]

        extra_kwargs = {
            'discount_code': {'required': True, "min_length": 3}
        }

    def validate(self, attrs):
        discount_type = attrs.get('discount_type')
        percent_off = attrs.get('percent_off')
        flat_rate_off = attrs.get('flat_rate_off')
        validate_discount_value_by_discount_type(False, discount_type, percent_off, flat_rate_off)
        return attrs

    def update(self, instance: CustomerLoyaltyDiscountSettings, validated_data: dict):
        pass


class LoyaltySettingsSerializer(BaseModelSerializerWithRequestObj):
    discount_settings = LoyaltyDiscountSettingsSerializer(many=True)

    class Meta:
        model = CustomerLoyaltySettings
        fields = [
            'is_active',
            'discount_settings'
        ]


class CustomerPointsSerializer(BaseModelSerializerWithRequestObj):
    class Meta:
        model = CustomerPoints
        exclude = ['businessman']
