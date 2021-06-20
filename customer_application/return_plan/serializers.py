from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj, BaseSerializerWithRequestObj
from common.util import create_field_error
from common.util.custom_validators import phone_validator
from customer_application.serializers import BusinessmanIdRelatedField, BaseBusinessmanSerializer
from customer_return_plan.models import Discount
from customer_return_plan.serializers import ReadOnlyDiscountSerializer
from customer_return_plan.services import customer_discount_service


class FriendInvitationSerializer(BaseSerializerWithRequestObj):
    businessman = BusinessmanIdRelatedField()
    friend_phone = serializers.CharField(max_length=20, validators=[phone_validator])
    friend_full_name = serializers.CharField(max_length=40)
    full_name = serializers.CharField(required=False, max_length=40)

    class Meta:
        fields = [
            'businessman',
            'friend_phone',
            'friend_full_name',
            'full_name'
        ]

        extra_kwargs = {'full_name': {'required': False}}

    def validate(self, attrs):
        user = self.request.user
        fn = attrs.get('full_name')
        if not user.is_full_name_set() and fn is None:
            err = create_field_error('full_name', ['نام کاربر اجباری است'])
            raise serializers.ValidationError(err)
        return attrs

    def validate_friend_phone(self, value):
        if value == self.request.user.phone:
            raise serializers.ValidationError("user phone and friend phone can not be same")
        return value


class CustomerReadonlyDiscountSerializer(ReadOnlyDiscountSerializer, BaseModelSerializerWithRequestObj):
    businessman = serializers.SerializerMethodField(read_only=True)
    is_invitation_and_usable = serializers.SerializerMethodField(read_only=True)

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
            'customers_used_total',
            'is_invitation_and_usable',
            'businessman'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = {}
        if kwargs.keys().__contains__('context'):
            context = {**kwargs.get('context')}
        context['customer'] = self.request.user

    def get_businessman(self, obj: Discount):
        return BaseBusinessmanSerializer(obj.businessman, request=self.request).data

    def get_is_invitation_and_usable(self, obj: Discount):
        result = customer_discount_service.is_invitation_inviter_discount_and_invited_has_purchase(
            obj,
            self.request.user
        )

        resp = {
            'is_invitation_discount': result[0],
            'is_customer_inviter': result[1],
            'invited_has_purchase': result[2],
            'invited_full_name': None,
            'invited_phone': None
        }

        if result[0] and result[1]:
            resp['invited_full_name'] = obj.inviter_discount.invited.customer.full_name
            resp['invited_phone'] = obj.inviter_discount.invited.customer.phone

        return resp
