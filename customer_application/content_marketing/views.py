from rest_framework import permissions
from rest_framework.request import Request

from base_app.permissions import AllowAnyOnGet
from common.util.http_helpers import ok, bad_request
from customer_application.base_views import BaseListAPIView, BaseAPIView
from customer_application.content_marketing.serializers import PostListSerializer, PostRetrieveSerializer, \
    CommentListCreateSerializer
from customer_application.content_marketing.services import customer_content_service
from customer_application.pagination import CustomerAppListPaginator


class ContentMarketingPagination(CustomerAppListPaginator):

    page_size = 12
    max_page_size = 20


class CommentsPageSize(CustomerAppListPaginator):

    page_size = 25
    max_page_size = 50


class PostsListAPIView(BaseListAPIView):

    pagination_class = ContentMarketingPagination
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        businessman_id = self.request.query_params.get('businessman_id')
        return customer_content_service.get_all_posts(businessman_id)

    def get_serializer_context(self):
        return {'request': self.request}


class PostRetrieveLikeAPIView(BaseAPIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, post_id: int):
        post = customer_content_service.retrieve_post_for_view(post_id, request.user)
        sr = PostRetrieveSerializer(post, request=request)
        return ok(sr.data)


class PostLike(BaseAPIView):

    def post(self, request: Request, post_id: int):
        post = customer_content_service.toggle_post_like(post_id, request.user)
        sr = PostRetrieveSerializer(post, request=request)
        return ok(sr.data)


class CommentsListCreateAPIView(BaseAPIView):

    permission_classes = [AllowAnyOnGet]

    def get(self, request, post_id: int):
        c = customer_content_service.get_post_comments(post_id)
        paginator = CommentsPageSize()
        page = paginator.paginate_queryset(c, request)
        sr = CommentListCreateSerializer(page, many=True, request=request)
        return paginator.get_paginated_response(sr.data)

    def post(self, request, post_id: int):
        sr = CommentListCreateSerializer(data=request.data, request=request)
        if not sr.is_valid():
            return bad_request(sr.errors)
        body = sr.validated_data.get('body')
        c = customer_content_service.add_comment(request.user, post_id, body)
        sr = CommentListCreateSerializer(c, request=request)
        return ok(sr.data)
