from base_app.serializers import BaseModelSerializerWithRequestObj, FileFieldWithLinkRepresentation
from content_marketing.models import Post


class PostListSerializer(BaseModelSerializerWithRequestObj):

    videofile = FileFieldWithLinkRepresentation(read_only=True)
    mobile_thumbnail = FileFieldWithLinkRepresentation(read_only=True)

    class Meta:
        model = Post
        fields = [
            'title',
            'videofile',
            'mobile_thumbnail',
            'likes_total',
            'views_total'
        ]


class PostRetrieveSerializer(PostListSerializer):

    class Meta:
        model = Post
        fields = [
            'title',
            'videofile',
            'mobile_thumbnail',
            'likes_total',
            'views_total',
            'description'
        ]
