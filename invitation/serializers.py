from rest_framework import serializers
from common.util.custom_validators import phone_validator
from invitation.models import FriendInvitation
from users.models import Customer


class FriendInvitationCreationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=15)
    invited_by = serializers.CharField(validators=[phone_validator])
    friend_phone = serializers.CharField(validators=[phone_validator])

    class Meta:
        fields = [
            'username'
            'invited_by',
            'friend_phone'
        ]


class FriendInvitationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'friend_phone',
            'invitation_date',
            'confirmed'
        ]


class InvitationBusinessmanListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendInvitation
        fields = [
            'id',
            'friend_phone',
            'confirmed',
            'invitation_date',
            'new',
        ]


class InvitationBusinessmanRetrieveSerializer(serializers.ModelSerializer):

    invited_by = serializers.CharField(max_length=15)

    class Meta:

        model = FriendInvitation
        fields = [
            'id',
            'friend_phone',
            'confirmed',
            'discount_used',
            'invitation_date',
            'invited_by'
        ]
