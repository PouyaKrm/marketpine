from rest_framework import serializers
from .models import Payment, PaymentTypes
from django.conf import settings


zarinpal_forward_link = settings.ZARINPAL.get('FORWARD_LINK')
constant_pay_amount = settings.ZARINPAL.get("CONSTANT_AMOUNT")

class PaymentCreationSerializer(serializers.ModelSerializer):
    '''serializer for payment app with geting amount'''
    forward_link = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'businessman',
            'authority',
            'forward_link'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'businessman': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'required': True},
                        'description': {'required': True},
                        }

    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)

    def get_forward_link(self, obj):
        return ('https://www.zarinpal.com/pg/StartPay/' + str(obj.authority)+'/ZarinGate')

    def create(self, validated_data):
        "create object payment with get amounte and constant businessman,phone,description"
        request = self.context['request']
        type = self.context['type']
        p = Payment.objects.create(businessman=request.user, phone=request.user.phone,
                                   payment_type=type,  **validated_data)
        p.pay(request)
        return p

class PaymentConstantAmountCreationSerializer(serializers.ModelSerializer):
    "serializer for result payment app with authority"

    forward_link = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'businessman',
            'authority',
            'forward_link'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'businessman': {'read_only': True},
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
                                   amount=constant_pay_amount, phone=request.user.phone,
                                   **validated_data)
        p.pay(request)
        return p

class PaymentResultSerializer(serializers.ModelSerializer):
    "serializer for result payment app with authority"

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'status',
            'creation_date',
            'authority',
            'refid',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'creation_date': {'read_only': True},
                        'status': {'read_only': True},
                        'amount': {'read_only': True},
                        'refid': {'read_only': True},
                        'authority': {'required': True},
                       }

class PaymentListSerializer(serializers.ModelSerializer):
    "serializer for list payment app with authority"

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'status',
            'authority',
            'refid',
            'creation_date',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'status': {'read_only': True},
                        'amount': {'read_only': True},
                        'refid': {'read_only': True},
                        'authority': {'read_only': True},
                        'creation_date': {'read_only': True},
                       }

class PaymentDetailSerializer(serializers.ModelSerializer):
    "serializer for list payment app with authority"

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'status',
            'authority',
            'refid',
            'creation_date',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'status': {'read_only': True},
                        'amount': {'read_only': True},
                        'refid': {'read_only': True},
                        'authority': {'read_only': True},
                        'creation_date': {'read_only': True},
                       }
