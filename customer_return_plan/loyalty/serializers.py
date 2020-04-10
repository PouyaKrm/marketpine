from rest_framework import serializers

from common.util import create_detail_error, create_field_error
from customer_return_plan.serializers import WritableNestedDiscountSettingSerializer
from .models import CustomerLoyaltyDiscountSettings, CustomerPurchaseAmountDiscountSettings, \
    CustomerPurchaseNumberDiscountSettings


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


class LoyaltySettingsSerializer(serializers.ModelSerializer):
    purchase_number_settings = PurchaseAmountSettingsSerializer(required=False)
    purchase_amount_settings = PurchaseNumberSettingsSerializer(required=False)

    class Meta:
        model = CustomerLoyaltyDiscountSettings
        fields = [
            'purchase_number_settings',
            'purchase_amount_settings',
            'disabled',
            'create_discount_for'
        ]

        extra_kwargs = {
            'disabled': {'required': True},
            'create_discount_for': {'required': True}
        }

    def validate(self, attrs: dict):
        number_att_name = 'purchase_number_settings'
        amount_att_name = 'purchase_amount_settings'
        discount_for = attrs.get('create_discount_for')
        number_setting = attrs.get(number_att_name)
        amount_setting = attrs.get(amount_att_name)
        amount_err = create_field_error(amount_att_name, ['تخفیف مقدار خرید اجباری است'])
        number_err = create_field_error(number_att_name, ['تخفیف تعداد خرید اجباری است'])
        if discount_for == CustomerLoyaltyDiscountSettings.FOR_PURCHASE_NUMBER and number_setting is None:
            raise serializers.ValidationError(number_err)
        if discount_for == CustomerLoyaltyDiscountSettings.FOR_PURCHASE_AMOUNT and amount_setting is None:
            raise serializers.ValidationError(amount_err)
        if discount_for == CustomerLoyaltyDiscountSettings.FOR_BOTH:
            err = {}
            if number_setting is None:
                err.update(**number_err)
            if amount_setting is None:
                err.update(**amount_err)
            raise serializers.ValidationError(err)
        return attrs

    def update(self, instance: CustomerLoyaltyDiscountSettings, validated_data: dict):
        number_settings = validated_data.pop('purchase_number_settings')
        amount_settings = validated_data.pop('purchase_amount_settings')
        discount_for = validated_data.get('create_discount_for')

        if discount_for == CustomerLoyaltyDiscountSettings.FOR_PURCHASE_NUMBER or discount_for == CustomerLoyaltyDiscountSettings.FOR_BOTH:
            for k, v in number_settings.items():
                setattr(instance.purchase_number_settings, k, v)
            instance.purchase_number_settings.save()

        if discount_for == CustomerLoyaltyDiscountSettings.FOR_PURCHASE_AMOUNT or discount_for == CustomerLoyaltyDiscountSettings.FOR_BOTH:
            for k, v in amount_settings.items():
                setattr(instance.purchase_amount_settings, k, v)
            instance.purchase_amount_settings.save()

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
