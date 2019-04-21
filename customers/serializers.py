from rest_framework import serializers
from users.models import Customer, Salesman, SalesmenCustomer
from rest_framework.validators import UniqueValidator
from users.serializers import phone_validator


class CustomerSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15, validators=[phone_validator])

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
        ]


class SalesmenCustomerSerializer(serializers.ModelSerializer):

    customer = CustomerSerializer()

    class Meta:

        model = SalesmenCustomer
        fields = [
            'id',
            'customer',
            'is_active',
            'register_date'
        ]

        extra_kwargs = {'is_active': {'read_only': True}}

    def validate_customer(self, value):

        phone = value.get('phone')

        result = Customer.objects.filter(phone=phone).count()
        user = self.context['request'].user

        if result > 0 and user.customers.filter(phone=phone).count() > 0:
            raise serializers.ValidationError('customer with this phone number already exists')

        return value

    def create(self, validated_data):

        phone = validated_data.get('customer').get('phone')

        if Customer.objects.filter(phone=phone).count() is 0:

            customer = Customer.objects.create(phone=phone)

        else:

            customer = Customer.objects.get(phone=phone)

        return SalesmenCustomer.objects.create(salesman=self.context['request'].user, customer=customer)

