from rest_framework import serializers

from customer_return_plan.models import Discount


class ReadOnlyDiscountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discount
        fields = [
            'discount_code',
            'expires',
            'expire_date',
            'discount_type',
            'percent_off',
            'flat_rate_off'
        ]
