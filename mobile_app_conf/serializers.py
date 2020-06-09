from rest_framework import serializers

from django.conf import settings

from common.util import create_link
from common.util.custom_validators import file_size_validator
from mobile_app_conf.models import MobileAppHeader, MobileAppPageConf

max_header_size = settings.MOBILE_APP_PAGE_CONF['MAX_HEADER_IMAGE_SIZE']


class FileFieldWithLinkRepresentation(serializers.FileField):

    def to_representation(self, value):
        return create_link(value.url, self.context['request'])


class MobileAppHeaderSerializer(serializers.ModelSerializer):

    header_image = FileFieldWithLinkRepresentation()

    class Meta:
        model = MobileAppHeader
        fields = [
            'header_image',
            'show_order'
        ]


    def validate_show_order(self, value):
        if MobileAppHeader.show_order_exists(value):
            raise serializers.ValidationError('show order already taken')
        return value

    def create(self, validated_data: dict):
        file = validated_data.get('header_image')
        request = self.context['request']
        show_order = validated_data.get('show_order')
        app_header = MobileAppPageConf.add_mobile_app_header(request.user, file, show_order)
        return {'file': create_link(app_header.header_image.url, request), 'show_order': app_header.show_order}


class MobileAppPageConfSerializer(serializers.ModelSerializer):

    headers = MobileAppHeaderSerializer(many=True, read_only=True)

    class Meta:
        model = MobileAppPageConf
        fields = [
            'headers',
            'market_location'
        ]

    def update(self, instance: MobileAppPageConf, validated_data: dict):
        instance.market_location = validated_data.get('market_location')
        instance.save()
        return validated_data

    def create(self, validated_data):
        pass

