import logging

from django.conf import settings
from django.db.models import QuerySet
from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj, BaseSerializerWithRequestObj
from common.util.kavenegar_local import APIException
from common.util.sms_panel.client import sms_client_management
from common.util.sms_panel.message import system_sms_message
from .models import Payment, PaymentTypes, SubscriptionPlan, Wallet
from .services import payment_service

zarinpal_forward_link = settings.ZARINPAL.get('FORWARD_LINK')
activation_pay_amount = settings.ACTIVATION_COST_IN_TOMANS
min_credit_charge = settings.SMS_PANEL['MIN_CREDIT_CHARGE']
max_allowed_credit = settings.SMS_PANEL['MAX_ALLOWED_CREDIT']
system_min_credit = settings.SMS_PANEL['SYSTEM_MIN_CREDIT']

wallet_minimum_credit_increase = settings.WALLET['MINIMUM_ALLOWED_CREDIT_INCREASE']


class BasePaymentCreationSerializer(BaseModelSerializerWithRequestObj):
    forward_link = serializers.SerializerMethodField(read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'authority',
            'forward_link'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'required': True},
                        }

    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)


class SMSCreditPaymentCreationSerializer(serializers.ModelSerializer):
    """erializer for payment app with geting amount"""
    forward_link = serializers.SerializerMethodField(read_only=True)
    amount = serializers.IntegerField(min_value=min_credit_charge)

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'authority',
            'forward_link'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'authority': {'read_only': True},
                        'amount': {'required': True},
                        }

    def validate_amount(self, value):
        err = serializers.ValidationError('امکان افزایش اعتبار با این مقدار نیست')
        request = self.context['request']
        if request.user.smspanelinfo.credit_in_tomans() + value > max_allowed_credit:
            raise err
        try:
            credit = sms_client_management.get_system_credit_in_tomans()
            available_credit = credit - system_min_credit / 10
            if available_credit < value:
                try:
                    system_sms_message.send_admin_low_system_credit_message()
                except APIException as e:
                    pass
                finally:
                    raise err
        except APIException as e:
            logging.error(e)
            raise serializers.ValidationError('خطای سیستم')
        return value

    def get_forward_link(self, obj):
        return zarinpal_forward_link.format(obj.authority)

    def create(self, validated_data):
        """create object payment with get amounte and constant businessman,phone,description"""
        request = self.context['request']
        p = Payment.objects.create(businessman=request.user, phone=request.user.phone,
                                   payment_type=PaymentTypes.SMS, **validated_data)
        p.pay(request)
        return p


class WalletIncreaseCreditSerializer(BasePaymentCreationSerializer):

    def validate_amount(self, value):
        if value < wallet_minimum_credit_increase:
            raise serializers.ValidationError(
                'حداقل میزان افزایش اعتبار {} تومان است'.format(
                    wallet_minimum_credit_increase
                )
            )

        return value


class PaymentResultSerializer(BaseModelSerializerWithRequestObj):
    class Meta:
        model = Payment
        fields = [
            'refid'
        ]


class SubscriptionPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class SubscriptionPlanField(serializers.RelatedField):

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


class SubscriptionPaymentCreationSerializer(BasePaymentCreationSerializer):
    "serializer for result payment app with authority"

    amount = serializers.IntegerField(read_only=True)
    plan = SubscriptionPlanField(required=True, write_only=True)

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
                        'description': {'read_only': True}
                        }


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


class WalletSerializer(BaseModelSerializerWithRequestObj):
    class Meta:
        model = Wallet
        fields = [
            'available_credit',
            'used_credit',
            'create_date',
            'update_date',
            'last_credit_increase_date',
            'has_subscription',
            'subscription_start',
            'subscription_end',
            'is_subscription_expired',
            'can_resubscribe',
        ]
        read_only_fields = [
            'available_credit',
            'used_credit',
            'create_date',
            'update_date',
            'last_credit_increase_date',
            'has_subscription',
            'subscription_start',
            'subscription_end',
            'is_subscription_expired',
            'can_resubscribe',
        ]


class BillingSummerySerializer(BaseSerializerWithRequestObj):
    create_date = serializers.CharField(max_length=50, read_only=True)
    amount = serializers.IntegerField(read_only=True)
    joined_by = serializers.CharField(max_length=10, read_only=True)
