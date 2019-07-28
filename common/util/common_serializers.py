from rest_framework import serializers

from common.util.custom_validators import phone_validator
from users.models import Customer


class CustomerSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone'
        ]