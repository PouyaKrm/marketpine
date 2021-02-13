from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from common.util.http_helpers import ok, bad_request, no_content
from content_marketing.services import content_marketing_service
from customer_application.base_views import BaseListAPIView, BaseAPIView
from customer_application.content_marketing.serializers import PostListSerializer, PostRetrieveSerializer
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

