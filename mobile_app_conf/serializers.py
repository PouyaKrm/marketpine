import ast

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework import serializers

from django.conf import settings

from base_app.serializers import BaseModelSerializerWithRequestObj, BaseSerializerWithRequestObj, \
    FileFieldWithLinkRepresentation
from common.util import create_link, get_client_ip, create_field_error
from common.util.custom_validators import file_size_validator, fixed_phone_line_or_cell_phone_validator
from common.util.gelocation import geolocation_service, LocationAPIException
from mobile_app_conf.models import MobileAppHeader, MobileAppPageConf, ContactInfo
from .services import mobile_page_conf_service

max_header_size = settings.MOBILE_APP_PAGE_CONF['MAX_HEADER_IMAGE_SIZE']
max_allowed_headers = settings.MOBILE_APP_PAGE_CONF['MAX_ALLOWED_HEADERS']


class MobileHeaderIdShowOrderField(serializers.Field):

    def to_internal_value(self, data) -> dict:
        if type(data) != str or len(data) > 100:
            raise serializers.ValidationError("invalid field")
        try:
            result = ast.literal_eval(data)
            if type(result) != dict:
                raise serializers.ValidationError("inavlid dictionary")
            return self._validate_items(result)
        except (SyntaxError, ValueError):
            raise serializers.ValidationError("invalid field")

    def _validate_items(self, id_show_orders: dict):
        user = self.context['request'].user
        if len(id_show_orders) > max_allowed_headers:
            raise serializers.ValidationError("invalid field")
        parsed_dict = {}
        for k, v in id_show_orders.items():
            try:
                k_int = int(k)
                v_int = int(v)
                if k_int <= 0:
                    raise serializers.ValidationError("{} is invalid id value".format(k_int))
                if not mobile_page_conf_service.header_id_exists_by_user(user, k_int):
                    raise serializers.ValidationError("header with id {} does not exist".format(k))
                parsed_dict[k_int] = v_int
            except ValueError:
                raise serializers.ValidationError("field contains un parsable to int values")

        if not mobile_page_conf_service.are_show_orders_unique_for_update(user, parsed_dict):
            raise serializers.ValidationError("some of show orders are already taken")

        return parsed_dict


class MobileAppHeaderSerializer(BaseModelSerializerWithRequestObj):
    header_image = FileFieldWithLinkRepresentation()
    updated_show_orders = MobileHeaderIdShowOrderField(write_only=True)

    class Meta:
        model = MobileAppHeader
        fields = [
            'id',
            'header_image',
            'show_order',
            'header_image_size',
            'updated_show_orders'
        ]
        extra_kwargs = {'show_order': {'required': True}, 'id': {'read_only': True},
                        'header_image_size': {'read_only': True}
                        }

    def validate_show_order(self, value):
        if not mobile_page_conf_service.can_upload_new_header(self.context['request'].user, value):
            raise serializers.ValidationError('can not upload image with new show order')
        return value

    def validate(self, attrs):
        show_order = attrs.get('show_order')
        updated_show_orders = attrs.get('updated_show_orders')
        if show_order in updated_show_orders.values():
            raise serializers.ValidationError("can not upload image with show order equal to show order in updated_show_orders")
        return attrs

    def create(self, validated_data: dict):
        file = validated_data.get('header_image')
        request = self.context['request']
        show_order = validated_data.get('show_order')
        updated_show_order = validated_data.get('updated_show_orders')
        mobile_page_conf_service.update_show_orders_of_headers(self.context['request'].user, updated_show_order)
        app_header = mobile_page_conf_service.add_mobile_app_header(request.user, file, show_order)
        return {'file': create_link(app_header.header_image.url, request), 'show_order': app_header.show_order,
                'header_image_size': app_header.header_image_size}


class ContactInfoSerializer(BaseSerializerWithRequestObj):

    phone = serializers.CharField(max_length=15, validators=[fixed_phone_line_or_cell_phone_validator])

    class Meta:
        model = ContactInfo
        fields = [
            'phone'
        ]


class MobileAppPageConfSerializer(BaseModelSerializerWithRequestObj):
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=1000)
    contact_info = ContactInfoSerializer(required=False, many=True)
    headers = MobileAppHeaderSerializer(many=True, read_only=True)
    ip_location = serializers.SerializerMethodField(read_only=True)
    page_id = serializers.CharField(required=False, allow_blank=True, min_length=6, max_length=20)
    instagram_page_url = serializers.URLField(required=False, allow_blank=True, max_length=200)

    class Meta:
        model = MobileAppPageConf
        fields = [
            'address',
            'is_address_set',
            'contact_info',
            'headers',
            'description',
            'location_lat',
            'location_lng',
            'is_location_set',
            'ip_location',
            'page_id',
            'instagram_page_url',
            'working_time_from',
            'working_time_to',
        ]

        extra_kwargs = {'is_address_set': {'read_only': True}}

    def get_ip_location(self, obj: MobileAppPageConf):
        if obj.is_location_set:
            return None
        ip = get_client_ip(self.request)
        try:
            return geolocation_service.get_location_by_ip(ip)
        except LocationAPIException as e:
            return None

    def validate_contact_info(self, value):
        if value is not None and len(value) > 3:
            raise serializers.ValidationError('3 contact info can be added at max')
        return value

    def validate_page_id(self, value):
        user = self.request.user
        if not mobile_page_conf_service.is_page_id_pattern_valid(value):
            raise serializers.ValidationError('فرمت اشتباه')
        elif not mobile_page_conf_service.is_page_id_unique(user, value):
            raise serializers.ValidationError('این آیدی صفحه قبلا استفاده شده')
        elif mobile_page_conf_service.is_page_id_predefined(value):
            raise serializers.ValidationError('آیدی غیر مجاز')
        return value

    def validate_instagram_page_url(self, value):
        mobile_page_conf_service.check_instagram_page_url_is_valid(value)
        return value

    def update(self, instance: MobileAppPageConf, validated_data: dict):
        pass

    def create(self, validated_data):
        pass
