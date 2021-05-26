import os

from django.db.models.base import Model
from django.core import validators
from django.template import TemplateSyntaxError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.util import create_link, create_field_error, create_detail_error
from common.util.custom_validators import sms_not_contains_link
from customers.services import customer_service
from panelprofile.services import sms_panel_info_service
from smspanel.models import SMSMessage, SMSMessageReceivers
from smspanel.services import SMSMessageService
from .models import Post, Comment, Like, ContentMarketingSettings
from common.util.custom_templates import get_fake_context, render_template, get_template_context
from django.conf import settings

from common.util.custom_validators import validate_file_size
from .services import content_marketing_service

template_min_chars = settings.SMS_PANEL['TEMPLATE_MIN_CHARS']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
thumbnail_max_chars = settings.CONTENT_MARKETING['THUMBNAIL_MAX_NAME_CHARS']
thumbnail_max_size = settings.CONTENT_MARKETING['THUMBNAIL_MAX_SIZE']


def validate_upload_video_size(file):
    if not validate_file_size(file, int(settings.CONTENT_MARKETING.get("MAX_SIZE_VIDEO"))):
        raise serializers.ValidationError(
            '({MAX_SIZE_VIDEO} byte.اندازه ویدیو بیشتر از حد مجاز است.(حداکثر مجاز می باشد'.format(
                max_size_video=settings.CONTENT_MARKETING.get("MAX_SIZE_VIDEO")
            ))

    return file


def validate_video_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = settings.CONTENT_MARKETING.get("ALLOWED_TYPES_VIDEO")
    if not ext.lower() in valid_extensions:
        raise serializers.ValidationError(u'Unsupported file extension.')
    else:
        return file


def validate_thumbnail_file_size(file):
    if not validate_file_size(file, thumbnail_max_size):
        raise serializers.ValidationError('اندازه لوگو بیش از حد مجاز است. حداکثر اندازه bytes {}'
                                          .format(thumbnail_max_size)
                                          )


class BasePostSerializer(serializers.ModelSerializer):
    video_link = serializers.SerializerMethodField(read_only=True)
    mobile_thumbnail_link = serializers.SerializerMethodField(read_only=True)
    likes_total = serializers.SerializerMethodField(read_only=True)
    comments_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'video_link',
            'mobile_thumbnail_link',
            'likes_total',
            'comments_total',
        ]

        extra_kwargs = {'id': {'read_only': True}}

    def get_video_link(self, obj: Post):
        return create_link(obj.videofile.url, self.context['request'])

    def get_mobile_thumbnail_link(self, obj: Post):
        return create_link(obj.mobile_thumbnail.url, self.context['request'])

    def get_likes_total(self, obj):
        return obj.likes.count()

    def get_comments_total(self, obj):
        return obj.comments.count()

    @staticmethod
    def serializer_fields():
        return BasePostSerializer.Meta.fields


class UploadListPostSerializer(BasePostSerializer):
    """serializer for Post app """

    videofile = serializers.FileField(max_length=254, write_only=True, validators=[
        validate_upload_video_size,
        validate_video_file_extension,
    ])

    title = serializers.CharField(min_length=5, max_length=100)
    mobile_thumbnail = serializers.ImageField(max_length=thumbnail_max_chars, required=True, write_only=True,
                                              validators=[validate_thumbnail_file_size])
    description = serializers.CharField(min_length=20, max_length=5000)
    notif_sms_template = serializers.CharField(required=False)
    send_sms = serializers.BooleanField(required=True)
    send_pwa = serializers.BooleanField(required=True)

    class Meta(BasePostSerializer.Meta):
        fields = BasePostSerializer.serializer_fields() + [
            'title',
            'description',
            'videofile',
            'confirmation_status',
            'mobile_thumbnail',
            'notif_sms_template',
            'send_sms',
            'send_pwa',
            'create_date'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'videofile': {'required': True},
                        'title': {'required': True},
                        'description': {'required': True},
                        'confirmation_status': {'read_only': True}
                        }

    def validate(self, attrs):
        sms_notif = attrs.get('send_sms')
        pwa_notif = attrs.get('send_pwa')
        template = attrs.get('notif_sms_template')
        request = self.context['request']
        if not sms_notif:
            return attrs

        if not sms_panel_info_service.has_valid_credit_to_send_to_all(request.user):
            raise ValidationError({'notif_sms_template': 'اعتبار کافی برای ارسال پیامک موجود نیست'})
        if template is None:
            raise serializers.ValidationError(create_field_error('notif_sms_template is required', ['template is required']))
        elif len(template) < template_min_chars or len(template) > template_max_chars:
            raise serializers.ValidationError(create_field_error('customer_notif_message_template',
                                                                 [f'templace length between {template_min_chars} and '
                                                                  f'{template_max_chars} characters']))

        sms_not_contains_link(template)
        return attrs

    def create(self, validated_data: dict):
        request = self.context['request']
        p = content_marketing_service.create_post(request, validated_data)
        return p
        # send_sms = validated_data.get('send_sms')
        # send_pwa = validated_data.get('send_pwa')
        # template = None
        # if send_sms:
        #     template = validated_data.pop('notif_sms_template')
        #
        # post = Post.objects.create(businessman=request.user, **validated_data)
        #
        # if send_sms:
        #     messenger = SendSMSMessage()
        #     post.notif_sms = messenger.content_marketing_message_status_cancel(user=request.user, template=template)
        # if send_pwa:
        #     post.send_pwa = True
        #     c = customer_service.get_businessman_customers(request.user)
        #     post.remaining_pwa_notif_customers.set(c)
        # post.video_url = create_link(post.videofile.url, request)
        # post.save()
        # return post




    # def update(self, instance: Post, validated_data: dict):
    #
    #     request = self.context['request']
    #
    #     instance.save(**validated_data)
    #     instance.video_url = create_link(instance.videofile.url, request)
    #     instance.save()
    #     return instance


class CommentSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'body',
            'create_date',
            'update_date',
            'customer'
        ]
        extra_kwargs = {'id': {'read_only': True}}


class DetailPostSerializer(BasePostSerializer):
    class Meta(BasePostSerializer.Meta):
        fields = BasePostSerializer.serializer_fields() + [
            'title',
            'description',
        ]


class DetailLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True},
                        }


class SetLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('id', 'post', 'customer',)

    # def validate_customer(self,value):
    #     customer = self.context['customer']
    #     if len(customer)> 0:
    #         raise serializers.ValidationError('.مشتری با این تلفن موجود نیست')
    #     return value
    #
    # def validate_post(self,value):
    #     post = self.context['post']
    #     if len(post) > 0:
    #         raise serializers.ValidationError('پستی با این id وجود ندارد.')
    #     return value
    def validate(self, value):
        post = self.context['post']
        customer = self.context['customer']
        if post.likes.filter(customer=customer).count() > 0:
            raise serializers.ValidationError('مشتری از قبل این پست را لایک کرده است.')

        return value

    def create(self, validated_data):
        post = self.context['post']
        customer = self.context['customer']
        return Like.objects.create(post=post,
                                   customer=customer,
                                   )


class SetCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'body': {'required': True},
                        }
        read_only_fields = ('id', 'post', 'customer',)

    def create(self, validated_data):
        post = self.context['post']
        customer = self.context['customer']
        return Comment.objects.create(post=post,
                                      customer=customer,
                                      **validated_data
                                      )


class ContentMarketingCreateRetrieveSerializer(serializers.ModelSerializer):
    message_template = serializers.CharField(min_length=5, max_length=template_max_chars, required=True)

    class Meta:
        model = ContentMarketingSettings
        fields = [
            'message_template',
            'send_video_upload_message'
        ]

        extra_kwargs = {'send_video_upload_message': {'required': True}}

    def validate_message_template(self, value):

        context = get_fake_context(self.context['user'])
        context.update(title='test title', link="http://testlink.com")

        try:
            render_template(value, context)
        except TemplateSyntaxError:
            raise serializers.ValidationError('قالب غیر مجاز')

        return value

    def create(self, validated_data: dict):

        user = self.context['user']

        return ContentMarketingSettings.objects.create(businessman=user, **validated_data)

    def update(self, instance: Model, validated_data: dict):

        user = self.context['user']

        if not hasattr(user, 'content_marketing_settings'):
            return self.create(validated_data)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance
