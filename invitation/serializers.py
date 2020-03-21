from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from common.util.custom_validators import phone_validator, sms_not_contains_link
from customers.serializers import CustomerListCreateSerializer
from invitation.models import FriendInvitation, FriendInvitationDiscount, FriendInvitationSettings
from common.util import common_serializers, DiscountType, generate_discount_code
from smspanel.services import SendSMSMessage
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
            user.customers.get(phone=value)
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
        invited_discount_code = generate_discount_code(DiscountType.INVITATION)
        inviter_discount_code = generate_discount_code(DiscountType.INVITATION)

        # user = self.context['user']
        user = self.context['user']
        invited = validated_data.get('invited')
        inviter = validated_data.get('inviter')
        inviter_customer = user.customers.get(phone=inviter)
        invited_customer = Customer.objects.create(businessman=user, phone=invited)

        obj = FriendInvitation(businessman=user, invited=invited_customer, inviter_discount_code=inviter_discount_code,
                               inviter=inviter_customer, invited_discount_code=invited_discount_code)

        invite_settings = user.friendinvitationsettings
        if invite_settings.is_percent_discount():
            obj.percent_off = invite_settings.percent_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_PERCENT
            obj.percent_off = invite_settings.percent_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_PERCENT

        else:
            obj.flat_rate_off = invite_settings.flat_rate_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_FLAT_RATE
            obj.flat_rate_off = invite_settings.flat_rate_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_FLAT_RATE

        # obj.save()

        sms = SendSMSMessage().friend_invitation_message(user, invite_settings.sms_template, invited_customer)
        obj.sms_message = sms
        obj.save()
        return {'id': obj.id, 'businessman': user.username, 'inviter': inviter, 'invited': invited,
                'invitation_date': obj.invitation_date, 'inviter_discount_code': obj.inviter_discount_code}


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
        invited_discount_code = generate_discount_code(DiscountType.INVITATION)
        inviter_discount_code = generate_discount_code(DiscountType.INVITATION)

        # user = self.context['user']
        user = self.user
        invited = validated_data.get('invited')
        inviter = validated_data.get('inviter')
        inviter_customer = user.customers.get(phone=inviter)
        invited_customer = Customer.objects.create(businessman=user, phone=invited)

        obj = FriendInvitation(businessman=user, invited=invited_customer, inviter_discount_code=inviter_discount_code,
                                              inviter=inviter_customer, invited_discount_code=invited_discount_code)
        # obj.invited_discount_code = invited_discount_code
        # obj.inviter_discount_code = inviter_discount_code

        # invited_discount = FriendInvitationDiscount.objects.create(friend_invitation=obj, customer=invited_customer,
        #                                         role=FriendInvitationDiscount.DISCOUNT_ROLE_INVITED, used=False,
        #                                         discount_code=invited_discount_code)
        # inviter_discount = FriendInvitationDiscount(friend_invitation=obj, customer=inviter_customer,
        #                          role=FriendInvitationDiscount.DISCOUNT_ROLE_INVITER, used=False,
        #                          discount_code=inviter_discount_code
        #                          )
        settings = FriendInvitationSettings.objects.get(businessman=user)

        pr = FriendInvitationSettings.percent_off
        invite_settings = self.user.friendinvitationsettings
        if settings.is_percent_discount():
            obj.percent_off = invite_settings.percent_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_PERCENT
            obj.percent_off = invite_settings.percent_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_PERCENT

        else:
            obj.flat_rate_off = invite_settings.flat_rate_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_FLAT_RATE
            obj.flat_rate_off = invite_settings.flat_rate_off
            obj.discount_type = invite_settings.DISCOUNT_TYPE_FLAT_RATE

        # obj.save()

        sms = SendSMSMessage().friend_invitation_message(user, settings.sms_template, invited_customer)
        obj.sms_message = sms
        obj.save()
        return {'id': obj.id, 'businessman': user.username, 'inviter': inviter, 'invited': invited,
                   'invitation_date': obj.invitation_date, 'inviter_discount_code': obj.inviter_discount_code}


    # def validate_invited(self, value):
    #
    #     user = self.context['user']
    #
    #     if user.customers.filter(phone=value).exists():
    #         raise serializers.ValidationError('این فرد قبلا معرفی شده است')
    #
    #     return value
    #
    # def validate_inviter(self, value):
    #
    #     user = self.context['user']
    #
    #     if not user.customers.filter(phone=value).exists():
    #         raise serializers.ValidationError('شماره مورد نظر در لیست مشتریان وجود ندارد')
    #
    #     return value
    #
    # def validate(self, data):
    #
    #     if data.get('invited')==data.get('inviter'):
    #         raise serializers.ValidationError({'details': ['امکان دعوت این مشتری وجود ندارد']})
    #
    #     return data


class FriendInvitationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'friend_phone',
            'invitation_date',
        ]


class InvitationBusinessmanListSerializer(serializers.ModelSerializer):
    invited = CustomerListCreateSerializer(read_only=True)

    inviter = CustomerListCreateSerializer(read_only=True)

    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'invitation_date',
            'invited',
            'inviter',
            'new',
        ]


class InvitationRetrieveSerializer(serializers.ModelSerializer):

    invited = common_serializers.CustomerSerializer(read_only=True)

    inviter = common_serializers.CustomerSerializer(read_only=True)

    class Meta:

        model = FriendInvitation
        fields = [
            'id',
            'invitation_date',
            'invited',
            'inviter'
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
        extra_kwargs = {'disabled': {'required': True}}

    def update(self, instance: FriendInvitationSettings, validated_data: dict):

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
