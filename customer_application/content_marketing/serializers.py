from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj, FileFieldWithLinkRepresentation
from content_marketing.models import Post, Comment
from content_marketing.services import content_marketing_service


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

    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'title',
            'videofile',
            'mobile_thumbnail',
            'likes_total',
            'is_liked',
            'views',
            'description',
        ]

    def get_is_liked(self, post: Post):
        return content_marketing_service.is_post_liked_by_customer(post, self.request.user)


class CommentListCreateSerializer(BaseModelSerializerWithRequestObj):

    body = serializers.CharField(max_length=150)

    class Meta:
        model = Comment
        fields = [
            'id',
            'body',
            'create_date'
        ]
