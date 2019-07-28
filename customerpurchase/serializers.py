from rest_framework import serializers
from customerpurchase.models import CustomerPurchase
from common.util.common_serializers import CustomerSerializer
from users.models import Customer


class PurchaseCreationSerializer(serializers.ModelSerializer):

    customer_id = serializers.IntegerField(min_value=1)

    class Meta:

        model = CustomerPurchase
        fields = [
            'id',
            'customer_id',
            'amount'
        ]

    def validate_customer_id(self, value):

        user = self.context['user']
        if not user.customers.filter(id=value).exists():
            raise serializers.ValidationError('این مشتری در لیست مشریان وجود ندارد')

        return value

    def create(self, validated_data):

        user = self.context['user']

        return CustomerPurchase.objects.create(businessman=user, **validated_data)

    def update(self, instance, validated_data):

        customer_id = validated_data.pop('customer_id')

        user = self.context['user']

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.customer = user.customers.get(id=customer_id)

        instance.save()

        return instance

class PurchaseListSerializer(serializers.ModelSerializer):

    customer = CustomerSerializer()

    class Meta:

        model = CustomerPurchase
        fields = [
            'id',
            'customer',
            'amount',
            'date'
        ]
