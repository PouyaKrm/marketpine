from django.db.models import QuerySet
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from common.util import create_field_error
from common.util.custom_validators import phone_validator
from customer_return_plan.models import Discount, BaseDiscountSettings
from customer_return_plan.services import DiscountService
from customers.services import CustomerService

discount_service = DiscountService()
customer_service = CustomerService()


class ReadOnlyDiscountSerializer(serializers.ModelSerializer):

    customers_used_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Discount
        fields = [
            'id',
            'discount_code',
            'expires',
            'expire_date',
            'discount_type',
            'used_for',
            'percent_off',
            'flat_rate_off',
            'customers_used_total'
        ]

    def get_customers_used_total(self, obj: Discount):
        return discount_service.get_num_of_customers_used_discount(obj)


class ReadOnlyDiscountWithUsedFieldSerializer(ReadOnlyDiscountSerializer):

    used_discount = serializers.SerializerMethodField(read_only=True)
    date_used = serializers.SerializerMethodField(read_only=True)
    # can_use = serializers.SerializerMethodField(read_only=True)

    class Meta(ReadOnlyDiscountSerializer.Meta):
        fields = ReadOnlyDiscountSerializer.Meta.fields + ['used_discount', 'date_used']

    def get_used_discount(self, discount: Discount):
        customer = self.context['customer']
        return discount_service.has_customer_used_discount(discount, customer)

    def get_date_used(self, obj: Discount):
        customer = self.context['customer']
        user = self.context['user']
        return discount_service.get_discount_date_used(user, obj, customer)

    # def get_can_use(self, obj: Discount):
    #     return discount_service.can_customer_use_discount(self.context['user'], obj, self.context['customer'])


class WritableDiscountCreateNestedSerializer(WritableNestedModelSerializer):
    discount_code = serializers.CharField(min_length=8, max_length=16, required=False)
    percent_off = serializers.FloatField(min_value=0, max_value=100)
    flat_rate_off = serializers.IntegerField(min_value=0),
    discount_type = serializers.CharField(max_length=2)
    auto_discount_code = serializers.BooleanField(write_only=True)


    class Meta:
        model = Discount
        fields = [
            'discount_code',
            'auto_discount_code',
            'discount_type',
            'percent_off',
            'flat_rate_off'
        ]

        extra_kwargs = {
            'discount_code': {'required': False},
            'auto_discount_code': {'required': True},
            'discount_type': {'required': True},
            'percent_off': {'required': True},
            'flat_rate_off': {'required': True},
        }

    def validate_discount_type(self, value):
        if value != Discount.DISCOUNT_TYPE_FLAT_RATE and value != Discount.DISCOUNT_TYPE_PERCENT:
            raise serializers.ValidationError('نوع تخفیف غیر مجاز است')
        return value

    def validate(self, attrs: dict):
        user = self.context['user']
        discount_type = attrs.get('discount_type')
        percent_off = attrs.get('percent_off')
        flat_rate_off = attrs.get('flat_rate_off')
        discount_code = attrs.get('discount_code')
        auto_discount_code = attrs.get('auto_discount_code')
        if not auto_discount_code and discount_code is None:
            raise serializers.ValidationError(create_field_error('discount_code', ['کد تخفیف داده اجباری است']))

        is_discount_code_unique = discount_service.is_discount_code_unique(user=user, code=discount_code)

        instance = self.context.get('discount_instance')

        if instance is not None and not auto_discount_code and instance.discount_code != discount_code and not is_discount_code_unique:
            raise serializers.ValidationError(create_field_error('discount_code', ['کد تخفیف یکتا نیست']))

        elif instance is None and not auto_discount_code and not is_discount_code_unique:
            raise serializers.ValidationError('کد تخفیف یکتا نیست')

        if discount_type == Discount.DISCOUNT_TYPE_PERCENT and percent_off <= 0:
            raise serializers.ValidationError(
                create_field_error('percent_off', ['مقدار تخفیف باید بزرگتر از صفر باشد']))
        if discount_type == Discount.DISCOUNT_TYPE_FLAT_RATE and flat_rate_off <= 0:
            raise serializers.ValidationError(
                create_field_error('flat_rate_off', ['مقدار تخفیف باید بزرگتر از صفر باشد']))
        return attrs

    def create_discount(self, expires: bool, auto_discount: bool, exp_date=None, **validated_data):
        user = self.context['user']
        discount = discount_service.create_discount(user, expires=expires, auto_discount_code=auto_discount,
                                                         expire_date=exp_date, **validated_data)
        return discount


class ApplyDiscountSerializer(serializers.Serializer):

    phone = serializers.CharField(max_length=15, validators=[phone_validator])
    discount_code = serializers.CharField(max_length=16, min_length=8)


    class Meta:

        fields = [
            'phone',
            'discount_code'
        ]

    def validate_phone(self, value):
        if not CustomerService().customer_exists(self.context['user'], value):
            raise serializers.ValidationError('مشتری با این شماره تلفن وجود ندارد')
        return value

    def validate_discount_code(self, value):
        user = self.context['user']
        if not discount_service.discount_exists_by_discount_code(user, value):
            raise serializers.ValidationError('کد تخفیف وجود معتبر نیست')
        return value


class WritableNestedDiscountSettingSerializer(WritableNestedModelSerializer):

    discount_type = serializers.CharField(required=True, max_length=2)
    percent_off = serializers.FloatField(required=True, min_value=0, max_value=100)
    flat_rate_off = serializers.IntegerField(required=True, min_value=0)

    class Meta:
        fields = [
            'discount_type',
            'percent_off',
            'flat_rate_off'
        ]

    def validate_discount_type(self, value):

        if value != BaseDiscountSettings.DISCOUNT_TYPE_PERCENT and value != BaseDiscountSettings.DISCOUNT_TYPE_FLAT_RATE:
            raise serializers.ValidationError('نوع تخفیف اشتباه است')
        return value

    def validate(self, attrs):
        discount_type = attrs.get('discount_type')
        percent_off = attrs.get('percent_off')
        flat_rate_off = attrs.get('flat_rate_off')

        if discount_type == BaseDiscountSettings.DISCOUNT_TYPE_PERCENT and percent_off <= 0:
            raise serializers.ValidationError(create_field_error('percent_off', ['مقدار تخفیف درصدی اشتباه است']))
        if discount_type == BaseDiscountSettings.DISCOUNT_TYPE_FLAT_RATE and flat_rate_off <= 0:
            raise serializers.ValidationError(create_field_error('flat_rate_off', ['مقدار تخفیف پولی اشتباه است']))
        return attrs


class DiscountReadIdListRepresentRelatedField(serializers.RelatedField):

    def get_queryset(self) -> QuerySet:
        return discount_service.get_businessman_all_discounts(self.context['user'])

    def to_internal_value(self, data) -> Discount:
        if type(data) != int or data <= 0:
            raise serializers.ValidationError('invalid id')
        result = discount_service.get_businessman_discount_or_none(self.context['user'], data)
        if result is None:
            raise serializers.ValidationError('not all discount ids exists')
        return result

    def to_representation(self, value: Discount):
        return ReadOnlyDiscountSerializer(value).data


