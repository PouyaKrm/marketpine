from rest_framework import serializers
from django.conf import settings

from base_app.serializers import ImageFiledWithLinkRepresentation, MultipartRequestBodyDictFiled, \
    BaseModelSerializerWithRequestObj
from common.util import create_link, create_detail_error
from .models import OnlineMenu
from common.util.custom_validators import file_size_validator
from .services import online_menu_service

max_file_size = settings.ONLINE_MENU['MAX_FILE_SIZE']
max_allowed_images = settings.ONLINE_MENU['MAX_ALLOWED_IMAGES']


class OnlineMenuSerializer(BaseModelSerializerWithRequestObj):
    #
    # file = serializers.ImageField(required=True, write_only=True, validators=[file_size_validator(max_file_size)])
    # file_link = serializers.SerializerMethodField(read_only=True)
    image = ImageFiledWithLinkRepresentation(required=True,
                                             validators=[file_size_validator(max_file_size)])
    new_show_orders = MultipartRequestBodyDictFiled(max_items=max_allowed_images, max_characters=200, write_only=True)

    class Meta:
        model = OnlineMenu
        fields = [
            # 'file',
            # 'file_link',
            'id',
            'image',
            'new_show_orders',
            'show_order'
        ]
    # def get_file_link(self, obj: OnlineMenu):
    #     return create_link(obj.file.url, self.context['request'])

    # def validate_new_show_orders(self, value):
    #     r = online_menu_service.are_new_show_orders_unique(value)
    #     if not r:
    #
    #     return value

    def validate(self, attrs):
        show_order = attrs.get('show_order')
        new_show_orders = attrs.get('new_show_orders')

        if show_order in new_show_orders.values():
            raise serializers.ValidationError(create_detail_error('show_order should not be in new_show_orders'))

        u = online_menu_service.are_new_show_orders_unique(show_order, new_show_orders)
        if not u:
            raise serializers.ValidationError('one of the new sho_orders are taken by other item wich is not'
                                              'provided in the new_show_orders')
        return attrs

    def create(self, validated_data: dict):
        pass
        # user = self.context['request'].user
        # validated_data.pop('new_show_orders')
        #
        # # OnlineMenu.objects.filter(businessman=user).delete()
        #     # menu = OnlineMenu.objects.get(businessman=user)
        #     # menu.delete()
        # # return OnlineMenu.objects.create(**validated_data, businessman=user)
        # return online_menu_service.add_image(user, **validated_data)

