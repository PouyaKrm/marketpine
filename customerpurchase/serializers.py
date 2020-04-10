from rest_framework import serializers

from common.util import create_field_error, create_detail_error
from customerpurchase.models import CustomerPurchase
from common.util.common_serializers import CustomerSerializer
from customers.services import CustomerService
from .services import purchase_service
from customer_return_plan.loyalty.services import loyalty_service

customer_service = CustomerService()


class PurchaseCreationUpdateSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(min_value=1)
    discount_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    amount = serializers.IntegerField(min_value=1)

    class Meta:

        model = CustomerPurchase
        fields = [
            'id',
            'customer_id',
            'amount',
            'discount_ids'
        ]

    def validate_customer_id(self, value):

        user = self.context['user']
        if not customer_service.customer_exists_by_id(user, value):
            raise serializers.ValidationError('این مشتری در لیست مشریان وجود ندارد')

        return value

    def validate(self, attrs):
        user = self.context['user']
        customer_id = attrs.get('customer_id')
        discount_ids = attrs.get('discount_ids')
        amount = attrs.get('amount')

        if discount_ids is None or len(discount_ids) == 0:
            return attrs

        result = purchase_service.validate_calculate_discount_amount_for_purchase(businessman=user,
                                                                                  customer_id=customer_id,
                                                                                  discount_ids=discount_ids,
                                                                                  purchase_amount=amount)

        if not result[0]:
            raise serializers.ValidationError(create_field_error('discount_ids', ['لیست تخفیف داده شده اشتباه است']))
        if result[0] and not result[1]:
            raise serializers.ValidationError(create_detail_error('مقدار تخفیف اعمال شده بیش از مقدار خرید است'))

        return attrs

    def create(self, validated_data):

        customer = customer_service.get_customer_by_id(validated_data.get('customer_id'))
        user = self.context['user']
        result = purchase_service.submit_purchase_with_discounts(user, **validated_data)
        loyalty_service.create_discount_for_loyalty(user, customer)
        return result[2]

    def update(self, instance, validated_data):

        customer_id = validated_data.pop('customer_id')

        user = self.context['user']

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.customer = user.customers.get(id=customer_id)

        instance.save()
        loyalty_service.re_evaluate_discounts_after_purchase_update_or_delete(user, instance.customer)

        return instance


class PurchaseListSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = CustomerPurchase
        fields = [
            'id',
            'customer',
            'amount',
            'create_date'
        ]


class CustomerPurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPurchase
        fields = [
            'id',
            'amount',
            'create_date'
        ]
