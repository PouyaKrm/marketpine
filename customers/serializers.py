from rest_framework import serializers

from common.util.custom_validators import phone_validator
from users.models import Customer


class CustomerSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15, validators=[phone_validator])

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'telegram_id',
            'instagram_id'
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}

    def validate_phone(self, value):

        user = self.context['user']

        if user.customers.filter(phone=value).count() > 0:

            raise serializers.ValidationError('another customer with this phone number already exists')

        return value

    def create(self, validated_data):

        return Customer.objects.create(businessman=self.context['user'], **validated_data)




# class SalesmenCustomerSerializer(serializers.ModelSerializer):
#
#     customer = CustomerSerializer()
#
#     class Meta:
#
#         model = SalesmenCustomer
#         fields = [
#             'id',
#             'customer',
#             'is_active',
#             'register_date'
#         ]
#
#         extra_kwargs = {'is_active': {'read_only': True}}

    #
    #
    # def validate_customer(self, value):
    #
    #     phone = value.get('phone')
    #
    #     result = Customer.objects.filter(phone=phone).count()
    #     user = self.context['request'].user
    #
    #     if result > 0 and user.customers.filter(phone=phone).count() > 0:
    #         raise serializers.ValidationError('customer with this phone number already exists')
    #
    #     return value
    #
    # def create(self, validated_data):
    #
    #     phone = validated_data.get('customer').get('phone')
    #
    #     if Customer.objects.filter(phone=phone).count() is 0:
    #
    #         customer = Customer.objects.create(phone=phone)
    #
    #     else:
    #
    #         customer = Customer.objects.get(phone=phone)
    #
    #     return SalesmenCustomer.objects.create(salesman=self.context['request'].user, customer=customer)
    #
