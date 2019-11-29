from rest_framework import serializers
from .models import Payment
from django.conf import settings

class PaymentCreationSerializer(serializers.ModelSerializer):
    '''serializer for payment app with geting amount'''

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'businessman',
            'authority',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'businessman': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'required': True},
                        'description': {'required': True},
                       }

    def create(self, validated_data):
        "create object payment with get amounte and constant businessman,phone,description"
        request=self.context['request']
        p = Payment.objects.create(businessman=request.user,
                                      phone=request.user.phone,
                                      **validated_data,
                                      )
        p.pay(request)
        return p


class PaymentConstantAmountCreationSerializer(serializers.ModelSerializer):
    "serializer for payment app with constant amount"

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'businessman',
            'authority',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'businessman': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'read_only': True,'required':False},
                        'description': {'required': True},
                       }
    def create(self, validated_data):
        "create object payment with constant amount,businessman,phone,description"
        request=self.context['request']
        p = Payment.objects.create(businessman=request.user,
                                      amount=settings.ZARINPAL.get("CONSTANT_AMOUNT"),
                                      phone=request.user.phone,
                                      **validated_data,
                                      )
        p.pay(request)
        return p
