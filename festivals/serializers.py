from django.template import TemplateSyntaxError
from django.utils import timezone
from rest_framework import serializers

from smspanel.services import SendSMSMessage
from users.models import Customer
from .models import Festival
from common.util.custom_validators import phone_validator, sms_not_contains_link

from django.conf import settings

template_min_chars = settings.SMS_PANEL['TEMPLATE_MIN_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']


class BaseFestivalSerializer(serializers.ModelSerializer):

    discount_code = serializers.CharField(min_length=8, max_length=12, required=True)
    message = serializers.CharField(required=True, min_length=template_min_chars, max_length=template_max_chars,
                                    validators=[sms_not_contains_link])
    name = serializers.CharField(required=True, min_length=5, max_length=20)
    customers_total = serializers.SerializerMethodField(read_only=True)
    percent_off = serializers.FloatField(min_value=0, max_value=100)

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            'discount_code',
            'message',
            'message_sent',
            'percent_off',
            'flat_rate_off',
            'customers_total'
        ]

        extra_kwargs = {'message_sent': {'read_only': True}}

    def validate_name(self, value):

        if self.context['user'].festival_set.filter(name=value).exists():
            raise serializers.ValidationError('name of the festival must be unique')

        return value

    def validate_start_date(self, value):

        if value < timezone.now().date():
            raise serializers.ValidationError('start date must be in present or future time')

        return value

    def validate_end_date(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError('end date must be in future time')

        return value

    def validate_flat_rate_off(self, value):

        if value < 0:
            raise serializers.ValidationError('invalid value')

        return value

    def validate_discount_code(self, value):

        user = self.context['user']

        if user.festival_set.filter(end_date__gte=timezone.now(), discount_code=value).exists():
            raise serializers.ValidationError('discount code must be unique')

        return value

    def validate(self, attrs):

        if attrs.get('start_date') >= attrs.get('end_date'):
            raise serializers.ValidationError({'end_date': ['end_date must be bigger than start_date']})

        return attrs

    def get_customers_total(self, obj: Festival):
        return obj.customers.count()


class FestivalCreationSerializer(BaseFestivalSerializer):

    class Meta(BaseFestivalSerializer.Meta):
        pass

    def create(self, validated_data):

        user = self.context['user']
        message = validated_data.pop('message')
        festival = Festival.objects.create(businessman=self.context['user'], **validated_data)
        festival.sms_message = SendSMSMessage().festival_message_status_cancel(message, user)
        festival.save()
        return {'id': festival.id, **validated_data, 'message': message}


class FestivalListSerializer(BaseFestivalSerializer):

    class Meta(BaseFestivalSerializer.Meta):

        BaseFestivalSerializer.Meta.fields.remove('message')


class RetrieveFestivalSerializer(BaseFestivalSerializer):

    message = serializers.CharField(min_length=template_min_chars, max_length=template_max_chars, source='sms_message.message')

    class Meta(BaseFestivalSerializer.Meta):
        pass

    def validate_name(self, value):
        if self.instance.name == value:
            return value
        return super().validate_name(value)

    def validate_discount_code(self, value):
        if self.instance.discount_code == value:
            return value
        return super().validate_discount_code(value)

    def update(self, instance: Festival, validated_data: dict):

        message = validated_data.pop('sms_message')['message']

        for key, val in validated_data.items():
            setattr(instance, key, val)

        SendSMSMessage().update_not_pending_message_text(instance.sms_message, message)

        instance.save()

        return {**validated_data, 'sms_message': {'message': message}}


class CustomerSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone'
        ]


class FestivalCustomerSerializer(serializers.Serializer):

    customer_phone = serializers.CharField(validators=[phone_validator])
    discount_code = serializers.CharField(min_length=8, max_length=12)

    class Meta:

        fields = [
            'customer_phone',
            'discount_code'
        ]

