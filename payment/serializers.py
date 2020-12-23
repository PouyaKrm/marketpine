from django.db.models import QuerySet
from rest_framework import serializers
from .models import Payment, PaymentTypes, PanelActivationPlans
from django.conf import settings

from .services import payment_service

zarinpal_forward_link = settings.ZARINPAL.get('FORWARD_LINK')
activation_pay_amount = settings.ACTIVATION_COST_IN_TOMANS
min_credit_charge = settings.SMS_PANEL['MIN_CREDIT_CHARGE']
max_credit_charge = settings.SMS_PANEL['MAX_CREDIT_CHARGE']
max_allowed_credit = settings.SMS_PANEL['MAX_ALLOWED_CREDIT']


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

    def validate_amount(self, value):
        request = self.context['request']
        if request.user.smspanelinfo.credit_in_tomans() + value > max_allowed_credit:
            raise serializers.ValidationError('امکان افزایش اعتبار با این مقدار نیست')
        return value

    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)

    def create(self, validated_data):
        """create object payment with get amounte and constant businessman,phone,description"""
        request = self.context['request']
        p = Payment.objects.create(businessman=request.user, phone=request.user.phone,
                                   payment_type=PaymentTypes.SMS,  **validated_data)
        p.pay(request)
        return p


class PanelActivationPlansSerializer(serializers.ModelSerializer):

    class Meta:
        model = PanelActivationPlans
        exclude = [
            'duration'
        ]

class PanelActivationPlanField(serializers.RelatedField):

    def to_internal_value(self, data):

        try:
            data = int(data)
            if data <= 0:
                raise serializers.ValidationError("invalid id field")
            if not payment_service.plan_exist_by_id(data):
                raise serializers.ValidationError("no plans exists by id")
            return payment_service.get_plan_by_id(data)
        except ValueError:
            raise serializers.ValidationError("id must be valid positive integer")

    def get_queryset(self) -> QuerySet:
        return payment_service.get_all_plans()


class PanelActivationPaymentCreationSerializer(serializers.ModelSerializer):
    "serializer for result payment app with authority"

    forward_link = serializers.SerializerMethodField(read_only=True)
    plan = PanelActivationPlanField(required=True, write_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'description',
            'authority',
            'forward_link',
            'plan'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'read_only': True, 'required': False},
                        'description': {'required': True},
                        }

    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)


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

