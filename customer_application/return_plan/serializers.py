from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj, BaseSerializerWithRequestObj
from common.util.custom_validators import phone_validator
from customer_application.serializers import BusinessmanIdRelatedField


class FriendInvitationSerializer(BaseSerializerWithRequestObj):

    businessman = BusinessmanIdRelatedField()
    friend_phone = serializers.CharField(max_length=20, validators=[phone_validator])

    class Meta:
        fields = [
            'businessman',
            'friend_phone'
        ]

    def validate_friend_phone(self, value):
        if value == self.request.user.phone:
            raise serializers.ValidationError("user phone and friend phone can not be same")
        return value
