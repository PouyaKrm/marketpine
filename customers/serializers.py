from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from common.util.custom_templates import CustomerTemplate
from common.util.custom_validators import phone_validator
# from common.util.sms_panel.message import SystemSMSMessage
from common.util.sms_panel.message import SystemSMSMessage
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.services import DiscountService, discount_service
from customerpurchase.services import PurchaseService
from customers.services import CustomerService
from smspanel.services import SendSMSMessage
from users.models import Customer
from django.db.models import Sum, QuerySet

message_service = SendSMSMessage()
customer_service = CustomerService()
purchase_service = PurchaseService()


class CustomerReadIdListRepresentRelatedField(serializers.RelatedField):

    """
    to use this custom related field, businessman should be provided
    with key "user" in context
    """

    def get_queryset(self) -> QuerySet:
        user = self.context['user']
        return customer_service.get_businessman_customers(user)

    def to_representation(self, value):
        serializer = CustomerListCreateSerializer(value, context=self.context)
        return serializer.data

    def to_internal_value(self, data) -> Customer:
        if type(data) != int or data <= 0:
            raise serializers.ValidationError("not valid primary key")
        # businessman = self.context['user']
        # query = Customer.objects.filter(businessman=businessman, id=data)
        # # r = query.count()
        # if not query.exists():
        #     raise serializers.ValidationError('not all customer ids are valid')
        # return query
        try:
            return customer_service.get_businessman_customer_by_id(self.context['user'], data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('not all customer ids are valid')


class CustomerListCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discount_service = DiscountService()

    phone = serializers.CharField(max_length=15, validators=[phone_validator])
    purchase_sum = serializers.SerializerMethodField(read_only=True)
    purchase_discount_sum = serializers.SerializerMethodField(read_only=True)
    has_discount = serializers.SerializerMethodField(read_only=True)
    invitations_total = serializers.SerializerMethodField(read_only=True)
    used_discounts_total = serializers.SerializerMethodField(read_only=True)
    invited_purchases_total = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'full_name',
            'telegram_id',
            'instagram_id',
            'purchase_sum',
            'purchase_discount_sum',
            'has_discount',
            'invitations_total',
            'used_discounts_total',
            'date_joined',
            'update_date',
            'invited_purchases_total'
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}

    def get_purchase_sum(self, obj):

        return purchase_service.get_customer_purchase_sum(self.context['user'], obj)

    def get_purchase_discount_sum(self, obj: Customer):
        user = self.context['user']
        purchases_total = purchase_service.get_customer_purchase_sum(user, obj)
        p_d =  discount_service.get_customer_used_discounts_sum_amount(self.context['user'], obj)
        return purchases_total - p_d

    def get_invitations_total(self, obj: Customer):
        return FriendInvitation.customer_total_invitations_count(obj)

    def get_used_discounts_total(self, obj: Customer):
        return discount_service.get_customer_used_discounts_for_businessman(self.context['user'], obj).count()

    def get_has_discount(self, obj: Customer):
        user = self.context['user']

        return self.discount_service.has_customer_any_discount(user, obj)

    def get_invited_purchases_total(self, obj: Customer):
        return FriendInvitation.customer_all_invited_friend_purchases_sum(self.context['user'], obj)

    def get_date_joined(self, obj: Customer):
        user = self.context['user']
        return customer_service.get_date_joined(obj, user)


    def validate_phone(self, value):

        user = self.context['user']

        if not customer_service.is_phone_number_unique_for_register(user, value):
            raise serializers.ValidationError('مشتری دیگری با این شماره تلفن قبلا ثبت شده')

        return value

    def create(self, validated_data):
        user = self.context['user']
        # if user.panelsetting.welcome_message is not None:
        #     message = CustomerTemplate(user, user.panelsetting.welcome_message, obj).render_template()
        #
        #     sms = SMSMessage()
        #
        #     sms.send_message(obj.phone, message)

        # return Customer().register(user, validated_data.get('phone'), validated_data.get('full_name'))
        return customer_service.add_customer(user, validated_data.get('phone'), validated_data.get('full_name'))


class CustomerSerializer(CustomerListCreateSerializer):

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'full_name',
            'telegram_id',
            'instagram_id',
            'purchase_sum',
            'purchase_discount_sum',
            'invitations_total',
            'used_discounts_total',
            'date_joined',
            'update_date',
            'invited_purchases_total'
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}

    # def get_purchase_sum(self, obj):
    #
    #     purchase = obj.customerpurchase_set.aggregate(purchase_sum=Sum('amount'))
    #
    #     return purchase['purchase_sum']

    def validate_phone(self, value):

        user = self.context['user']

        customer_id = self.context.get('customer_id')
        c = customer_service.get_businessman_customer_by_id(user, customer_id)

        if not customer_service.is_phone_number_unique_for_update(user, c, value):
            raise serializers.ValidationError('مشتری دیگری با این شماره تلفن قبلا ثبت شده')

        return value

    def update(self, instance: Customer, validated_data):
        return instance
        # old_phone = instance.phone
        # new_phone = validated_data.get('phone')
        # user = self.context['user']
        #
        # for k, v in validated_data.items():
        #
        #     setattr(instance, k, v)
        #
        # instance.save()
        #
        # if (new_phone != old_phone) and (user.panelsetting.welcome_message is not None):
        #     message = CustomerTemplate(user, user.panelsetting.welcome_message, instance).render_template()
        #
        #     sms = SystemSMSMessage()
        #
        #     sms.send_message(new_phone, message)
        #
        # return instance

    def create(self, validated_data):
        pass
