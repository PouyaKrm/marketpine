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
            'full_name',
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

