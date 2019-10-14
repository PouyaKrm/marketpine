from rest_framework import serializers

from common.util.custom_templates import CustomerTemplate
from common.util.custom_validators import phone_validator
from common.util.sms_panel import SystemSMSMessage
from users.models import Customer
from django.db.models import Sum


class CustomerListCreateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15, validators=[phone_validator])
    purchase_sum = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'full_name',
            'telegram_id',
            'instagram_id',
            'purchase_sum',
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}

    def get_purchase_sum(self, obj):

        purchase = obj.customerpurchase_set.aggregate(purchase_sum=Sum('amount'))

        return purchase['purchase_sum']

    def validate_phone(self, value):

        user = self.context['user']

        if user.customers.filter(phone=value).count() > 0:
            raise serializers.ValidationError('مشتری دیگری با این شماره تلفن قبلا ثبت شده')

        return value

    def create(self, validated_data):
        user = self.context['user']

        obj = Customer.objects.create(businessman=user, **validated_data)
        # if user.panelsetting.welcome_message is not None:
        #     message = CustomerTemplate(user, user.panelsetting.welcome_message, obj).render_template()
        #
        #     sms = SMSMessage()
        #
        #     sms.send_message(obj.phone, message)

        return obj


class CustomerSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15, validators=[phone_validator])
    purchase_sum = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'full_name',
            'telegram_id',
            'instagram_id',
            'purchase_sum',
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}


    def get_purchase_sum(self, obj):

        purchase = obj.customerpurchase_set.aggregate(purchase_sum=Sum('amount'))

        return purchase['purchase_sum']

    def validate_phone(self, value):

        user = self.context['user']

        customer_id = self.context.get('customer_id')

        if user.customers.exclude(id=customer_id).filter(phone=value).count() > 0:
            raise serializers.ValidationError('مشتری دیگری با این شماره تلفن قبلا ثبت شده')

        return value


    def update(self, instance: Customer, validated_data):

        old_phone = instance.phone
        new_phone = validated_data.get('phone')
        user = self.context['user']

        for k, v in validated_data.items():

            setattr(instance, k, v)

        instance.save()

        if (new_phone != old_phone) and (user.panelsetting.welcome_message is not None):
            message = CustomerTemplate(user, user.panelsetting.welcome_message, instance).render_template()

            sms = SystemSMSMessage()

            sms.send_message(new_phone, message)

        return instance
