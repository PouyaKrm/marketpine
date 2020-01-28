from django.urls import path
from rest_framework import serializers

from common.util import create_link
from .models import Post , Comment , Like
from common.util.file_validators import validate_upload_video_size , validate_file_extension
from users.models import Businessman,Customer
from common.util.custom_validators import phone_validator


class UploadListPostSerializer(serializers.ModelSerializer):
    """serializer for Post app """


    videofile = serializers.FileField(max_length=254, write_only=True, validators=[
                                                        validate_upload_video_size,
                                                        validate_file_extension,
                                                        ])
    video = serializers.SerializerMethodField(read_only=True)
    likes_total = serializers.SerializerMethodField(read_only=True)
    comments_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'videofile',
            'is_confirmed',
            'video',
            'likes_total',
            'comments_total'
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'videofile': {'required': True},
                        'title': {'required': True},
                        'description': {'required': True}
                        }


    def get_video(self, obj: Post):

        return create_link(obj.videofile.url, self.context['request'])

    def get_likes_total(self, obj):
        return obj.likes.count()

    def get_comments_total(self, obj):
        return obj.comments.count()


    def create(self, validated_data):
        request = self.context['request']

        return Post.objects.create(businessman=request.user, is_confirmed=False, **validated_data)


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
    def validate(self,value):
        post = self.context['post']
        customer = self.context['customer']
        if post.likes.filter(customer = customer).count() > 0:
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
