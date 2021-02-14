from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj, FileFieldWithLinkRepresentation
from content_marketing.models import Post, Comment
from content_marketing.services import content_marketing_service
from customer_application.serializers import BaseBusinessmanSerializer


class PostListSerializer(BaseModelSerializerWithRequestObj):

    videofile = FileFieldWithLinkRepresentation(read_only=True)
    mobile_thumbnail = FileFieldWithLinkRepresentation(read_only=True)
    businessman = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'title',
            'videofile',
            'mobile_thumbnail',
            'likes_total',
            'views',
            'businessman',
        ]

    def get_businessman(self, post: Post):
        return BaseBusinessmanSerializer(post.businessman, request=self.request).data


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
            'businessman',
            'description',
        ]

    def get_is_liked(self, post: Post):
        return content_marketing_service.is_post_liked_by_customer(post, self.request.user)


class CommentListCreateSerializer(BaseModelSerializerWithRequestObj):

    body = serializers.CharField(max_length=150)
    belongs_to = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'body',
            'belongs_to',
            'create_date',
        ]

    def get_belongs_to(self, comment: Comment):
        return comment.customer == self.request.user
