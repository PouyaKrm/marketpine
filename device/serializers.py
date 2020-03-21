from rest_framework import serializers

from users.models import Customer
from common.util.custom_validators import phone_validator


class CustomerRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15,validators=[phone_validator], required=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',

        ]
        extra_kwargs = {'id': {'read_only': True}}

    def validate_phone(self, value):
        user = self.context['user']
        if Customer.objects.filter(businessman=user, phone=value).exists():
            raise serializers.ValidationError('این مشتری قبلا ثبت شده')
        return value

    def create(self, validated_data):

        user = self.context['user']
        return Customer.objects.create(businessman=user, **validated_data)


