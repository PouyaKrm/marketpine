from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from common.util.custom_validators import phone_validator, sms_not_contains_link
from customer_return_plan.serializers import ReadOnlyDiscountSerializer
from customer_return_plan.services import DiscountService
from customers.serializers import CustomerListCreateSerializer, CustomerSerializer
from customer_return_plan.invitation.models import FriendInvitation, FriendInvitationSettings
from common.util import common_serializers, DiscountType, generate_discount_code, create_field_error
from customers.services import customer_service
from smspanel.services import SMSMessageService
from users.models import Customer, Businessman

from django.conf import settings

template_min_chars = settings.SMS_PANEL['TEMPLATE_MIN_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']


class BaseFriendInvitationSerializer(serializers.Serializer):
    inviter = serializers.CharField(validators=[phone_validator])
    invited = serializers.CharField(validators=[phone_validator])

    class Meta:
        fields = [
            'inviter',
            'invited'
        ]

    def validate_inviter(self, value):
        user = self.context['user']
        try:
            customer_service.get_customer_by_businessman_and_phone(user, value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('مشتری با این شماره تلفن وجود ندارد')
        return value

    def validate_invited(self, value):
        user = self.context['user']
        if user.customers.filter(phone=value).exists():
            raise serializers.ValidationError('این مشتری قبلا معرفی شده')
        return value

    def validate(self, attrs):
        inviter = attrs.get('inviter')
        invited = attrs.get('invited')
        if inviter == invited:
            raise serializers.ValidationError()

        return attrs

    def create(self, validated_data: dict):
        user = self.context['user']
        invited = validated_data.get('invited')
        inviter = validated_data.get('inviter')
        inviter_customer = customer_service.get_customer_by_businessman_and_phone(user, phone=inviter)
        invited_customer = customer_service.add_customer(user, invited)

        invitation = FriendInvitation(businessman=user, inviter=inviter_customer, invited=invited_customer)

        settings = FriendInvitationSettings.objects.get(businessman=user)

        invite_settings = user.friendinvitationsettings

        service = DiscountService()
        inviter_discount = service.create_discount(user, False, invite_settings.discount_type, True,
                                                   percent_off=invite_settings.percent_off,
                                                   flat_rate_off=invite_settings.flat_rate_off
                                                   )

        invited_discount = service.create_invitation_discount(user, False, invite_settings.discount_type, True,
                                                              percent_off=invite_settings.percent_off,
                                                              flat_rate_off=invite_settings.flat_rate_off
                                                              )

        invitation.inviter_discount = inviter_discount
        invitation.invited_discount = invited_discount

        sms = SMSMessageService().friend_invitation_message(user, settings.sms_template, invited_customer)
        invitation.sms_message = sms
        invitation.save()
        return {'id': invitation.id, 'businessman': user.username, 'inviter': invitation.inviter.phone,
                'invited': invitation.invited.phone,
                'invitation_date': invitation.create_date,
                'inviter_discount_code': invitation.inviter_discount.discount_code}


class FriendInvitationCreationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=15)
    inviter = serializers.CharField(validators=[phone_validator])
    invited = serializers.CharField(validators=[phone_validator])

    def __init__(self, data):
        super().__init__(data=data)

        username = data.get('username')
        if username is None:
            return
        self.user = Businessman.objects.get(username=username)

    class Meta:
        fields = [
            'username'
            'inviter',
            'invited'
        ]

    def validate_inviter(self, value):
        # user = self.context['user']
        user = self.user
        try:
            user.customers.get(phone=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('مشتری با این شماره تلفن وجود ندارد')
        return value

    def validate_invited(self, value):
        # user = self.context['user']
        user = self.user
        if user.customers.filter(phone=value).exists():
            raise serializers.ValidationError('این مشتری قبلا معرفی شده')
        return value

    def validate(self, attrs):
        inviter = attrs.get('inviter')
        invited = attrs.get('invited')
        if inviter == invited:
            raise serializers.ValidationError()

        return attrs

    def create(self, validated_data: dict):
        user = self.user
        invited = validated_data.get('invited')
        inviter = validated_data.get('inviter')
        inviter_customer = customer_service.get_customer_by_businessman_and_phone(user, phone=inviter)
        invited_customer = customer_service.add_customer(businessman=user, phone=invited)

        invitation = FriendInvitation(businessman=user, inviter=inviter_customer, invited=invited_customer)

        settings = FriendInvitationSettings.objects.get(businessman=user)

        invite_settings = user.friendinvitationsettings

        service = DiscountService()
        inviter_discount = service.create_discount(user, False, invite_settings.discount_type, True,
                                                   percent_off=invite_settings.percent_off,
                                                   flat_rate_off=invite_settings.flat_rate_off
                                                   )

        invited_discount = service.create_invitation_discount(user, False, invite_settings.discount_type, True,
                                                              percent_off=invite_settings.percent_off,
                                                              flat_rate_off=invite_settings.flat_rate_off
                                                              )

        invitation.inviter_discount = inviter_discount
        invitation.invited_discount = invited_discount

        sms = SMSMessageService().friend_invitation_message(user, settings.sms_template, invited_customer)
        invitation.sms_message = sms
        invitation.save()
        return {'id': invitation.id, 'businessman': user.username, 'inviter': invitation.inviter.phone,
                'invited': invitation.invited.phone,
                'invitation_date': invitation.create_date,
                'inviter_discount_code': invitation.inviter_discount.discount_code}


class FriendInvitationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'friend_phone',
            'invitation_date',
        ]


class InvitationBusinessmanListSerializer(serializers.ModelSerializer):
    inviter = CustomerListCreateSerializer(read_only=True)
    invited = CustomerListCreateSerializer(read_only=True)

    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'create_date',
            'inviter',
            'invited',
            'new',
        ]


class InvitationRetrieveSerializer(InvitationBusinessmanListSerializer):
    inviter_discount = ReadOnlyDiscountSerializer(read_only=True)
    invited_discount = ReadOnlyDiscountSerializer(read_only=True)

    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'create_date',
            'inviter',
            'invited',
            'new',
            'inviter_discount',
            'invited_discount',
        ]


class FriendInvitationSettingsSerializer(serializers.ModelSerializer):
    sms_template = serializers.CharField(required=True, min_length=template_min_chars, max_length=template_max_chars,
                                         validators=[sms_not_contains_link])
    flat_rate_off = serializers.IntegerField(required=True, min_value=0)
    percent_off = serializers.FloatField(required=True, min_value=0, max_value=100)

    class Meta:
        model = FriendInvitationSettings
        fields = [
            'sms_template',
            'disabled',
            'percent_off',
            'discount_type',
            'flat_rate_off'
        ]
        extra_kwargs = {
            'disabled': {'required': True},
            'discount_type': {'required': True}
        }

    def validate_discount_type(self, value):
        if value != FriendInvitationSettings.DISCOUNT_TYPE_PERCENT and value != FriendInvitationSettings.DISCOUNT_TYPE_FLAT_RATE:
            raise serializers.ValidationError('مقدار نوع تخفیف غیر مجاز است')
        return value

    def validate(self, attrs):
        percent_off = attrs.get('percent_off')
        flat_rate_off = attrs.get('flat_rate_off')
        discount_type = attrs.get('discount_type')

        if discount_type == FriendInvitationSettings.DISCOUNT_TYPE_FLAT_RATE and flat_rate_off <= 0:
            raise serializers.ValidationError(
                create_field_error('flat_rate_off', ['مقدار تخفیف پولی باید بزرگتر از صفر باشد']))
        if discount_type == FriendInvitationSettings.DISCOUNT_TYPE_PERCENT and percent_off <= 0:
            raise serializers.ValidationError(
                create_field_error('flat_rate_off', ['مقدار تخفیف درصدی باید بزرگتر از صفر باشد']))

        return attrs

    def update(self, instance: FriendInvitationSettings, validated_data: dict):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

