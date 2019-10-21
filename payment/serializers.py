from rest_framework import serializers
from .models import Payment


class PaymentCreationSerializer(serializers.ModelSerializer):
    '''serializer for payment app with geting amount'''

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'amount': {'required': True},
                       }

    def create(self, validated_data):
        "create object payment with get amounte and constant businessman,phone,description"
        request=self.context['request']
        return Payment.objects.create(businessman=request.user,
                                      phone=request.user.phone,
                                      description="creation test",
                                      **validated_data,
                                      )



class PaymentFixAmountCreationSerializer(serializers.ModelSerializer):
    "serializer for payment app without amount"

    class Meta:
        model = Payment
        fields = [
            'id',
        ]
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        "create object payment with constant amount,businessman,phone,description"
        request=self.context['request']
        return Payment.objects.create(businessman=request.user,
                                      amount="123456",
                                      phone=request.user.phone,
                                      description="tset for default amount",
                                      **validated_data,
                                      )
