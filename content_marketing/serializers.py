from rest_framework import serializers
from .models import Video
from common.util.file_validators import validate_upload_video
from users.models import Businessman

class VideoSerializer(serializers.ModelSerializer):
    '''serializer for video app '''
    videofile = serializers.FileField(max_length = 254,validators = [validate_upload_video])
    class Meta:
        model = Video
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

        return Video.objects.create(businessman=request.user,
                                    **validated_data,
                                    )
