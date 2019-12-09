from rest_framework import serializers
from .models import Post , Comment
from common.util.file_validators import validate_upload_video_size , validate_file_extension
from users.models import Businessman

class PostSerializer(serializers.ModelSerializer):
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
            # 'businessman',
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
    '''serializer for Post app '''

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'videofile',
            'businessman',
            'likers',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'videofile': {'required':True},
                        'title' : {'required' : True},
                       }


class DetailCommentSerializer(serializers.ModelSerializer):
    '''serializer for Post app '''

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True},
                       }
