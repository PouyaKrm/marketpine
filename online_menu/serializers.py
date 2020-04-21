from rest_framework import serializers
from django.conf import settings

from common.util import create_link
from .models import OnlineMenu
from common.util.custom_validators import file_size_validator

max_file_size = settings.ONLINE_MENU['MAX_FILE_SIZE']


class OnlineMenuSerializer(serializers.ModelSerializer):

    file = serializers.ImageField(required=True, write_only=True, validators=[file_size_validator(max_file_size)])
    file_link = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OnlineMenu
        fields = [
            'file',
            'file_link',
            'create_date',
        ]

    def get_file_link(self, obj: OnlineMenu):
        return create_link(obj.file.url, self.context['request'])

    def create(self, validated_data: dict):
        user = self.context['request'].user
        OnlineMenu.objects.filter(businessman=user).delete()
            # menu = OnlineMenu.objects.get(businessman=user)
            # menu.delete()
        return OnlineMenu.objects.create(**validated_data, businessman=user)
