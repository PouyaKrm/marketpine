from django.utils import timezone
from rest_framework import serializers
from users.models import Customer
from .models import Festival
from common.util.custom_validators import phone_validator


class FestivalCreationSerializer(serializers.ModelSerializer):

    discount_code = serializers.CharField(min_length=8, max_length=12, required=True)

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            'is_general',
            'discount_code',
            'percent_off',
            'flat_rate_off'
        ]


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




    def validate(self, attrs):

        if attrs.get('start_date') >= attrs.get('end_date'):
            raise serializers.ValidationError({'end_date': ['end_date must be bigger than start_date']})

        return attrs



    def validate_percent_off(self, value):

        if not ((value >= 0) and (value <= 100)):
            raise serializers.ValidationError('invalid value')

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


    def create(self, validated_data):

        return Festival.objects.create(businessman=self.context['user'], **validated_data)


class FestivalListSerializer(serializers.ModelSerializer):

    customers_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'customers_total'
        ]

    def get_customers_total(self, obj: Festival):
        return obj.customers.count()





class RetrieveFestivalSerializer(serializers.ModelSerializer):

    customers_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Festival
        fields = [

            'id',
            'name',
            'start_date',
            'end_date',
            'is_general',
            'discount_code',
            'percent_off',
            'flat_rate_off',
            'customers_total'

        ]

    def get_customers_total(self, obj: Festival):
        return obj.customers.count()

    def validate_name(self, value):

        if self.context['user'].festival_set.exclude(id=self.context['festival_id']).filter(name=value).exists():
            raise serializers.ValidationError('name of the festival must be unique')

        return value



    def update(self, instance: Festival, validated_data):

        instance.name = validated_data.get('name')

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

    # def validate_discount_code(self, value):
    #
    #     user = self.context['user']
    #
    #     if not user.festival_set.filter(discount_code=value).exists():
    #         raise serializers.ValidationError('discount_code does not exists')
    #
    #     return value
    #
    # def validate_phone(self, value):
    #
    #     user = self.context['user']
    #
    #     if not user.customers.filter(phone=value).exists():
    #         raise serializers.ValidationError('customer does not exists')
    #
    #     return value
    #