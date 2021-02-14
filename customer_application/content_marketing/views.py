from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from base_app.permissions import AllowAnyOnGet
from common.util.http_helpers import ok, bad_request, no_content
from content_marketing.services import content_marketing_service
from customer_application.base_views import BaseListAPIView, BaseAPIView
from customer_application.content_marketing.serializers import PostListSerializer, PostRetrieveSerializer, \
    CommentListCreateSerializer
from customer_application.content_marketing.services import customer_content_service
from customer_application.exceptions import CustomerServiceException
from customer_application.pagination import CustomerAppListPaginator


class ContentMarketingPagination(CustomerAppListPaginator):

    page_size = 12
    max_page_size = 20


class PostsListAPIView(BaseListAPIView):

    pagination_class = ContentMarketingPagination
    serializer_class = PostListSerializer

    def get_queryset(self):
        return content_marketing_service.get_all_posts()


class PostRetrieveLikeAPIView(BaseAPIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, post_id: int):
        try:
            post = customer_content_service.retrieve_post_for_view(post_id, request.user)
            sr = PostRetrieveSerializer(post, request=request)
            return ok(sr.data)
        except CustomerServiceException as e:
            return bad_request(e.http_message)


class PostLike(BaseAPIView):

    def post(self, request: Request, post_id: int):
        try:
            post = customer_content_service.toggle_post_like(post_id, request.user)
            sr = PostRetrieveSerializer(post, request=request)
            return ok(sr.data)
        except CustomerServiceException as e:
            return bad_request(e.http_message)


class CommentsListCreateAPIView(BaseAPIView):

    permission_classes = [AllowAnyOnGet]

    def get(self, request, post_id: int):
        try:
            c = customer_content_service.get_post_comments(post_id)
            paginator = CustomerAppListPaginator()
            page = paginator.paginate_queryset(c, request)
            sr = CommentListCreateSerializer(page, many=True)
            return paginator.get_paginated_response(sr.data)
        except CustomerServiceException as e:
            return bad_request(e.http_message)

    def post(self, request, post_id: int):
        sr = CommentListCreateSerializer(data=request.data)
        if not sr.is_valid():
            return bad_request(sr.errors)
        try:
            body = sr.validated_data.get('body')
            c = customer_content_service.add_comment(request.user, post_id, body)
            sr = CommentListCreateSerializer(c)
            return ok(sr.data)
        except CustomerServiceException as e:
            return bad_request(e.http_message)
