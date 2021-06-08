from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework import serializers

from base_app.serializers import BusinessmanGroupRelatedField
from common.util.custom_validators import phone_validator
# from common.util.sms_panel.message import SystemSMSMessage
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.services import DiscountService, discount_service
from customerpurchase.services import PurchaseService
from customers.services import CustomerService
from smspanel.services import SMSMessageService
from users.models import Customer

message_service = SMSMessageService()
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
            return customer_service.get_businessman_customer_by_id(self.context['user'], data, "customer")
        except ObjectDoesNotExist:
            raise serializers.ValidationError('not all customer ids are valid')


class CustomerListCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discount_service = DiscountService()

    phone = serializers.CharField(max_length=15, validators=[phone_validator])
    groups = BusinessmanGroupRelatedField(write_only=True, required=False, many=True)
    purchase_sum = serializers.SerializerMethodField(read_only=True)
    purchase_discount_sum = serializers.SerializerMethodField(read_only=True)
    has_discount = serializers.SerializerMethodField(read_only=True)
    invitations_total = serializers.SerializerMethodField(read_only=True)
    used_discounts_total = serializers.SerializerMethodField(read_only=True)
    invited_purchases_total = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.SerializerMethodField(read_only=True)
    can_edit_info = serializers.SerializerMethodField(read_only=True)
    is_member_of_group = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'groups',
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
            'invited_purchases_total',
            'can_edit_info',
            'is_member_of_group'
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}

    def get_purchase_sum(self, obj):

        return purchase_service.get_customer_purchase_sum(self.context['user'], obj)

    def get_purchase_discount_sum(self, obj: Customer):
        user = self.context['user']
        purchases_total = purchase_service.get_customer_purchase_sum(user, obj)
        p_d = discount_service.get_customer_used_discounts_sum_amount(self.context['user'], obj)
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

    def get_can_edit_full_name(self, obj: Customer):
        user = self.context['user']
        return customer_service.can_edit_full_name(user, obj)

    def get_can_edit_info(self, obj: Customer):
        return not obj.is_phone_confirmed

    def get_is_member_of_group(self, obj: Customer):
        from groups.models import BusinessmanGroups
        user = self.context['user']
        group_id = self.context.get('check_member_group_id')
        if group_id is None:
            return False
        return BusinessmanGroups.is_member_of_group(user, obj, group_id)

    def validate_phone(self, value):

        user = self.context['user']

        if not customer_service.is_phone_number_unique_for_register(user, value):
            raise serializers.ValidationError('مشتری دیگری با این شماره تلفن قبلا ثبت شده')

        return value

    def create(self, validated_data):
        user = self.context['user']
        phone = validated_data.get('phone')
        full_name = validated_data.get('full_name')
        groups = validated_data.get('groups')
        # if user.panelsetting.welcome_message is not None:
        #     message = CustomerTemplate(user, user.panelsetting.welcome_message, obj).render_template()
        #
        #     sms = SMSMessage()
        #
        #     sms.send_message(obj.phone, message)

        # return Customer().register(user, validated_data.get('phone'), validated_data.get('full_name'))
        return customer_service.add_customer(user, phone, full_name, groups)


class CustomerSerializer(CustomerListCreateSerializer):

    phone = serializers.CharField(required=False, max_length=15, validators=[phone_validator])
    joined_groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'groups',
            'full_name',
            'telegram_id',
            'instagram_id',
            'purchase_sum',
            'purchase_discount_sum',
            'invitations_total',
            'used_discounts_total',
            'date_joined',
            'update_date',
            'invited_purchases_total',
            'can_edit_info',
            'joined_groups',
        ]

        extra_kwargs = {'telegram_id': {'read_only': True}, 'instagram_id': {'read_only': True}}

    def get_joined_groups(self, obj: Customer):
        from groups.serializers import BusinessmanGroupsCreateListSerializer
        sr = BusinessmanGroupsCreateListSerializer(obj.connected_groups, many=True)
        return sr.data

    def update(self, instance: Customer, validated_data):
      pass

    def create(self, validated_data):
        pass

