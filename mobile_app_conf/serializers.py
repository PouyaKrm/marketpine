from rest_framework import serializers

from django.conf import settings

from common.util import create_link
from common.util.custom_validators import file_size_validator
from mobile_app_conf.models import MobileAppHeader, MobileAppPageConf

max_header_size = settings.MOBILE_APP_PAGE_CONF['MAX_HEADER_IMAGE_SIZE']


class MobileAppHeaderSerializer(serializers.Serializer):

    file = serializers.ImageField(required=True, write_only=True, validators=[file_size_validator(max_header_size)])

    class Meta:
        fields = [
            'file'
        ]

    def create(self, validated_data: dict):
        file = validated_data.get('file')
        request = self.context['request']
        app_header = MobileAppPageConf.add_mobile_app_header(request.user, file)
        return {'file': create_link(app_header.header_image.url, request)}
