import os

from django.db.models.base import Model
from django.template import TemplateSyntaxError
from rest_framework import serializers

from common.util import create_link
from .models import Post , Comment , Like, ContentMarketingSettings
from common.util.custom_templates import get_fake_context, render_template
from django.conf import settings

from common.util.custom_validators import validate_file_size

template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
template_min_chars = settings.SMS_PANEL['TEMPLATE_MIN_CHARS']
thumbnail_max_chars = settings.CONTENT_MARKETING['THUMBNAIL_MAX_NAME_CHARS']
thumbnail_max_size = settings.CONTENT_MARKETING['THUMBNAIL_MAX_SIZE']




def validate_upload_video_size (file):
    if not validate_file_size(file, int(settings.CONTENT_MARKETING.get("MAX_SIZE_VIDEO"))):
        raise serializers.ValidationError(
        '({MAX_SIZE_VIDEO} byte.اندازه ویدیو بیشتر از حد مجاز است.(حداکثر مجاز می باشد'.format(
        max_size_video =settings.CONTENT_MARKETING.get("MAX_SIZE_VIDEO")
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


class UploadListPostSerializer(serializers.ModelSerializer):
    """serializer for Post app """


    videofile = serializers.FileField(max_length=254, write_only=True, validators=[
                                                        validate_upload_video_size,
                                                        validate_video_file_extension,
                                                        ])
    video_link = serializers.SerializerMethodField(read_only=True)
    mobile_thumbnail_link = serializers.SerializerMethodField(read_only=True)
    likes_total = serializers.SerializerMethodField(read_only=True)
    comments_total = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(min_length=5, max_length=40)
    mobile_thumbnail = serializers.ImageField(max_length=thumbnail_max_chars, required=True, write_only=True,
                                              validators=[validate_thumbnail_file_size])

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'videofile',
            'confirmation_status',
            'video_link',
            'mobile_thumbnail_link',
            'mobile_thumbnail',
            'likes_total',
            'comments_total'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'videofile': {'required': True},
                        'title': {'required': True},
                        'description': {'required': True}
                        }


    def get_video_link(self, obj: Post):

        return create_link(obj.videofile.url, self.context['request'])

    def get_mobile_thumbnail_link(self, obj: Post):
        return create_link(obj.mobile_thumbnail.url, self.context['request'])

    def get_likes_total(self, obj):
        return obj.likes.count()

    def get_comments_total(self, obj):
        return obj.comments.count()


    def create(self, validated_data):
        request = self.context['request']

        post = Post.objects.create(businessman=request.user, **validated_data)
        post.video_url = create_link(post.videofile.url, request)
        post.save()
        return post


class CommentSerializer(serializers.ModelSerializer):

    customer = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'body',
            'creation_date',
            'customer'
        ]
        extra_kwargs = {'id': {'read_only': True}}


class DetailPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'videofile',
            'businessman'
        ]
        extra_kwargs = {'id': {'read_only': True},
                       }



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
        read_only_fields = ('id','post','customer',)

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
        return Like.objects.create(post = post,
                                   customer = customer,
                                  )

class SetCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'body': {'required': True},
                       }
        read_only_fields = ('id','post','customer',)

    def create(self, validated_data):
        post = self.context['post']
        customer = self.context['customer']
        return Comment.objects.create(post = post,
                                      customer = customer,
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



