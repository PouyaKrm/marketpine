from rest_framework import serializers

from common.util import create_field_error, create_detail_error
from customer_return_plan.models import Discount
from customer_return_plan.services import DiscountService
from customerpurchase.models import CustomerPurchase
from common.util.common_serializers import CustomerSerializer
from customers.services import CustomerService
from customers.serializers import CustomerReadIdListRepresentRelatedField
from .services import purchase_service
from customer_return_plan.loyalty.services import loyalty_service
from customer_return_plan.serializers import DiscountReadIdListRepresentRelatedField

customer_service = CustomerService()
discount_service = DiscountService()


class PurchaseCreationUpdateSerializer(serializers.ModelSerializer):
    # customer_id = serializers.IntegerField(min_value=1)
    customer = CustomerReadIdListRepresentRelatedField(required=True)
    # discount_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    discounts = DiscountReadIdListRepresentRelatedField(many=True, required=False, write_only=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:

        model = CustomerPurchase
        fields = [
            'id',
            # 'customer_id',
            'amount',
            'discounts',
            'customer'
        ]

    def validate_customer_id(self, value):

        user = self.context['user']
        if not customer_service.customer_exists_by_id(user, value):
            raise serializers.ValidationError('این مشتری در لیست مشریان وجود ندارد')

        return value

    def validate(self, attrs):
        user = self.context['user']
        # customer_id = attrs.get('customer_id')
        customer = attrs.get('customer')
        discounts = attrs.get('discounts')
        amount = attrs.get('amount')

        if discounts is None or len(discounts) == 0:
            return attrs

        result = purchase_service.validate_calculate_discount_amount_for_purchase(discounts=discounts,
                                                                                  purchase_amount=amount)
        can_use = False
        for discount in discounts:
            can_use = discount_service.can_customer_use_discount(user, discount, customer)
            if can_use is False:
                break

        if not result[0] or not can_use:
            raise serializers.ValidationError(create_field_error('discounts', ['لیست تخفیف داده شده اشتباه است']))
        if result[0] and not result[1]:
            raise serializers.ValidationError(create_detail_error('مقدار تخفیف اعمال شده بیش از مقدار خرید است'))

        return attrs

    def create(self, validated_data):

        user = self.context['user']
        # customer = customer_service.get_customer_by_id(user, validated_data.get('customer_id'))
        customer = validated_data.get('customer')
        amount = validated_data.get('amount')
        discounts = validated_data.get('discounts')
        # result = purchase_service.submit_purchase_with_discounts(user, **validated_data)
        result = purchase_service.add_customer_purchase(user, customer, amount)
        discount_service.try_apply_discounts(user, discounts, result)
        return result

    def update(self, instance, validated_data):

        customer_id = validated_data.pop('customer_id')

        user = self.context['user']

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.customer = user.customers.get(id=customer_id)

        instance.save()
        # loyalty_service.re_evaluate_discounts_after_purchase_update_or_delete(user, instance.customer)

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
