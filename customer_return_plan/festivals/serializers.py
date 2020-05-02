from django.template import TemplateSyntaxError
from django.utils import timezone
from drf_writable_nested import NestedUpdateMixin
from rest_framework import serializers

from common.util import generate_discount_code, DiscountType
from customer_return_plan.festivals.services import FestivalService
from customer_return_plan.services import DiscountService
from smspanel.services import SendSMSMessage
from users.models import Customer
from .models import Festival
from common.util.custom_validators import phone_validator, sms_not_contains_link

from customer_return_plan.serializers import WritableDiscountCreateNestedSerializer

from django.conf import settings

template_min_chars = settings.SMS_PANEL['TEMPLATE_MIN_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
festival_service = FestivalService()
discount_service = DiscountService()

class BaseFestivalSerializer(serializers.ModelSerializer):
    # discount_code = serializers.CharField(min_length=8, max_length=12, required=True)
    message = serializers.CharField(required=True, min_length=template_min_chars, max_length=template_max_chars,
                                    validators=[sms_not_contains_link])
    name = serializers.CharField(required=True, min_length=5, max_length=20)

    # percent_off = serializers.FloatField(min_value=0, max_value=100)
    discount = WritableDiscountCreateNestedSerializer()

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            # 'discount_code',
            'message',
            'message_sent',
            # 'percent_off',
            # 'flat_rate_off',
            'discount'
        ]

        extra_kwargs = {'message_sent': {'read_only': True}}

    @staticmethod
    def get_fields_excluded_from(*args) -> list:
        """
        returns fields that are provided field names are excluded from original fields
        :param args: name of the fields to be excluded
        :return: new list of fields that does not contains excluded fields provided in argument
        """
        fields = BaseFestivalSerializer.Meta.fields.copy()
        for f in args:
            fields.remove(f)
        return fields

    def validate_name(self, value):

        if festival_service.festival_by_name_exists(self.context['user'], value):
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

    # def validate_flat_rate_off(self, value):
    #
    #     if value < 0:
    #         raise serializers.ValidationError('invalid value')
    #
    #     return value

    # def validate_discount_code(self, value):
    #
    #     user = self.context['user']
    #
    #     if user.festival_set.filter(end_date__gte=timezone.now(), discount_code=value).exists():
    #         raise serializers.ValidationError('discount code must be unique')
    #
    #     return value

    def validate(self, attrs):

        if attrs.get('start_date') >= attrs.get('end_date'):
            raise serializers.ValidationError({'end_date': ['end_date must be bigger than start_date']})

        return attrs


class FestivalCreationSerializer(BaseFestivalSerializer):
    class Meta(BaseFestivalSerializer.Meta):
        pass

    def create(self, validated_data):
        user = self.context['user']
        message = validated_data.pop('message')
        discount_data = validated_data.pop('discount')
        festival = Festival.objects.create(businessman=self.context['user'], **validated_data)
        festival.sms_message = SendSMSMessage().festival_message_status_cancel(message, user)
        festival.discount = discount_service.create_festival_discount(user=user,
                                                                           expires=True,
                                                                           expire_date=festival.end_date,
                                                                           **discount_data)

        festival.save()
        return {'id': festival.id, **validated_data, 'message': message, 'discount': discount_data}


class FestivalListSerializer(serializers.ModelSerializer):
    customers_total = serializers.SerializerMethodField(read_only=True)
    discount_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            'customers_total',
            'discount_code'
        ]

    def get_customers_total(self, obj: Festival):
        return discount_service.get_total_customers_used_festival_discount(obj)

    def get_discount_code(self, obj: Festival):
        return obj.discount.discount_code


class RetrieveFestivalSerializer(NestedUpdateMixin, BaseFestivalSerializer):
    message = serializers.CharField(min_length=template_min_chars, max_length=template_max_chars,
                                    source='sms_message.message')
    discount = WritableDiscountCreateNestedSerializer()


    class Meta(BaseFestivalSerializer.Meta):
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            'discount',
            'message',
        ]

    def validate_name(self, value):
        if self.instance.name == value:
            return value
        return super().validate_name(value)

    def validate_start_date(self, value):
        if value >= self.instance.start_date:
            return value
        return super().validate_start_date(value)

    # def validate_discount_code(self, value):
    #     if self.instance.discount_code == value:
    #         return value
    #     return super().validate_discount_code(value)

    def update(self, instance: Festival, validated_data: dict):

        message = validated_data.pop('sms_message')['message']
        discount_data = validated_data.pop('discount')

        for key, val in validated_data.items():
            setattr(instance, key, val)

        SendSMSMessage().update_not_pending_message_text(instance.sms_message, message)

        discount_service.update_discount(discount=instance.discount, expires=True, expire_date=instance.end_date,
                                              user=instance.businessman, **discount_data)

        instance.save()

        return instance


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
