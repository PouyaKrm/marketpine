from rest_framework import serializers
from .models import Post , Comment , Like
from common.util.file_validators import validate_upload_video_size , validate_file_extension
from users.models import Businessman,Customer
from common.util.custom_validators import phone_validator

class UploadPostSerializer(serializers.ModelSerializer):
    '''serializer for Post app '''
    videofile = serializers.FileField(max_length = 254,validators = [
                                                        validate_upload_video_size,
                                                        validate_file_extension,
                                                        ])
    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'videofile',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'videofile': {'required':True},
                        'title' : {'required' : True},
                       }

    def create(self, validated_data):
        request = self.context['request']

        return Post.objects.create(businessman=request.user,
                                    **validated_data,
                                    )

class DetailPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'videofile',
            'businessman',
        ]
        extra_kwargs = {'id': {'read_only': True},
                       }

class DetailCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
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
