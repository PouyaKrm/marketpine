from rest_framework import serializers
from .models import Payment, PaymentTypes
from django.conf import settings


zarinpal_forward_link = settings.ZARINPAL.get('FORWARD_LINK')
activation_pay_amount = settings.ACTIVATION_COST_IN_TOMANS
min_credit_charge = settings.SMS_PANEL['MIN_CREDIT_CHARGE']
max_credit_charge = settings.SMS_PANEL['MAX_CREDIT_CHARGE']


class SMSCreditPaymentCreationSerializer(serializers.ModelSerializer):
    """erializer for payment app with geting amount"""
    forward_link = serializers.SerializerMethodField(read_only=True)
    amount = serializers.IntegerField(min_value=min_credit_charge, max_value=max_credit_charge)

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'authority',
            'forward_link'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'required': True},
                        'description': {'required': True},
                        }


    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)

    def create(self, validated_data):
        """create object payment with get amounte and constant businessman,phone,description"""
        request = self.context['request']
        p = Payment.objects.create(businessman=request.user, phone=request.user.phone,
                                   payment_type=PaymentTypes.SMS,  **validated_data)
        p.pay(request)
        return p


class PanelActivationPaymentCreationSerializer(serializers.ModelSerializer):
    "serializer for result payment app with authority"

    forward_link = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'authority',
            'forward_link'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'read_only': True, 'required': False},
                        'description': {'required': True},
                        }


    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)

    def create(self, validated_data):
        "create object payment with constant amount,businessman,phone,description"
        request=self.context['request']
        p = Payment.objects.create(businessman=request.user, payment_type=PaymentTypes.ACTIVATION,
                                   amount=activation_pay_amount, phone=request.user.phone,
                                   **validated_data)
        p.pay(request)
        return p


class PaymentListSerializer(serializers.ModelSerializer):
    "serializer for list payment app with authority"

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'verification_status',
            'refid',
            'verification_date',
            'payment_type'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'verification_status': {'read_only': True},
                        'amount': {'read_only': True},
                        'refid': {'read_only': True},
                        'verification_date': {'read_only': True},
                        }


