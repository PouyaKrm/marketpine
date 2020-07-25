from rest_framework import serializers

from django.conf import settings

from base_app.serializers import BaseModelSerializerWithRequestObj
from common.util import create_link, get_client_ip
from common.util.custom_validators import file_size_validator
from common.util.gelocation import geolocation_service, LocationAPIException
from mobile_app_conf.models import MobileAppHeader, MobileAppPageConf
from .services import mobile_page_conf_service

max_header_size = settings.MOBILE_APP_PAGE_CONF['MAX_HEADER_IMAGE_SIZE']


class FileFieldWithLinkRepresentation(serializers.FileField):

    def to_representation(self, value):
        return create_link(value.url, self.context['request'])


class MobileAppHeaderSerializer(serializers.ModelSerializer):

    header_image = FileFieldWithLinkRepresentation()

    class Meta:
        model = MobileAppHeader
        fields = [
            'id',
            'header_image',
            'show_order',
            'header_image_size',
        ]
        extra_kwargs = {'show_order': {'required': True}, 'id': {'read_only': True},
                        'header_image_size': {'read_only': True}
                        }

    def validate_show_order(self, value):
        if not mobile_page_conf_service.can_upload_new_header(self.context['request'].user, value):
            raise serializers.ValidationError('can not upload image with new show order')
        return value

    def create(self, validated_data: dict):
        file = validated_data.get('header_image')
        request = self.context['request']
        show_order = validated_data.get('show_order')
        app_header = mobile_page_conf_service.add_mobile_app_header(request.user, file, show_order)
        return {'file': create_link(app_header.header_image.url, request), 'show_order': app_header.show_order,
                'header_image_size': app_header.header_image_size}


class MobileAppPageConfSerializer(BaseModelSerializerWithRequestObj):

    headers = MobileAppHeaderSerializer(many=True, read_only=True)
    ip_location = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MobileAppPageConf
        fields = [
            'headers',
            'description',
            'location_lat',
            'location_lng',
            'is_location_set',
            'ip_location'
        ]

    def get_ip_location(self, obj: MobileAppPageConf):
        if obj.is_location_set:
            return None
        ip = get_client_ip(self.request)
        try:
            return geolocation_service.get_location_by_ip(ip)
        except LocationAPIException as e:
            return None

    def update(self, instance: MobileAppPageConf, validated_data: dict):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return validated_data

    def create(self, validated_data):
        pass

