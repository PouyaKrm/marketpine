from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj, BaseSerializerWithRequestObj
from common.util import create_field_error
from common.util.custom_validators import phone_validator
from customer_application.serializers import BusinessmanIdRelatedField, BaseBusinessmanSerializer, \
    customer_full_name_field
from customer_return_plan.models import Discount
from customer_return_plan.serializers import ReadOnlyDiscountSerializer


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = {}
        if kwargs.keys().__contains__('context'):
            context = {**kwargs.get('context')}
        context['customer'] = self.request.user

    class Meta(ReadOnlyDiscountSerializer.Meta):
        fields = ['businessman'] + ReadOnlyDiscountSerializer.Meta.fields.copy()

    def get_businessman(self, obj: Discount):
        return BaseBusinessmanSerializer(obj.businessman, request=self.request).data
