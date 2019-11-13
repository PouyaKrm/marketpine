from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    '''serializer for video app '''

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'description',
            'videofile',
        ]
        extra_kwargs = {'id': {'read_only': True},
                       }
