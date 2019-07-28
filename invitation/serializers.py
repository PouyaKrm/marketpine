from rest_framework import serializers
from common.util.custom_validators import phone_validator
from invitation.models import FriendInvitation
from common.util import common_serializers


class FriendInvitationCreationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=15)
    inviter = serializers.CharField(validators=[phone_validator])
    invited = serializers.CharField(validators=[phone_validator])

    class Meta:
        fields = [
            'username'
            'inviter',
            'invited'
        ]


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
    invited = common_serializers.CustomerSerializer(read_only=True)

    inviter = common_serializers.CustomerSerializer(read_only=True)

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


