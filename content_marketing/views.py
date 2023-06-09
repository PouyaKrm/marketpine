from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.error_codes import ApplicationErrorException
from base_app.views import BaseListAPIView
from common.util.http_helpers import ok, no_content, bad_request
from smspanel.permissions import HasActiveSMSPanel
from users.models import Customer
from .models import Post
from .permissions import DoesNotHavePendingPostForUpload
from .serializers import (UploadListPostSerializer, DetailPostSerializer,
                          CommentSerializer, DetailLikeSerializer,
                          SetCommentSerializer, SetLikeSerializer,
                          ContentMarketingCreateRetrieveSerializer
                          )
from .services import content_marketing_service

video_page_size = settings.CONTENT_MARKETING['VIDEO_PAGINATION_PAGE_SIZE']


@api_view(['POST'])
def set_comment_post(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    customer = get_object_or_404(Customer, phone=request.data['phone'])
    serializer = SetCommentSerializer(data=request.data,context={'post': post,'customer':customer})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def set_like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    customer = get_object_or_404(Customer, phone=request.data['phone'])

    serializer = SetLikeSerializer(data=request.data,context={'post': post,'customer':customer})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def detail_comment_post(request, post_id):
    post = content_marketing_service.get_post_by_id_or_404(request.user, post_id)
    comments = post.comments.all()
    serializer = CommentSerializer(comments, many=True)
    return ok(serializer.data)


@api_view(['GET'])
def detail_like_post(request, post_id):
    post = content_marketing_service.get_post_by_id_or_404(request.user, post_id)
    likes = post.likes.all()
    serializer = DetailLikeSerializer(likes, many=True)
    return ok(serializer.data)


class PostCreateListAPIView(CreateAPIView, ListModelMixin):
    parser_class = (FileUploadParser,)
    serializer_class = UploadListPostSerializer
    permission_classes = [permissions.IsAuthenticated,
                          HasActiveSMSPanel,
                          DoesNotHavePendingPostForUpload,
                          ]
    pagination_class = PageNumberPagination
    pagination_class.page_size = video_page_size

    def get_queryset(self):
        return content_marketing_service.get_businessman_all_posts(self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request: Request, *args, **kwargs) -> Response:

        try:
            return super().create(request, *args, **kwargs)
        except ApplicationErrorException as e:
            print(e.http_message)
            return bad_request(e.http_message)


class PostRetrieveDeleteAPIView(APIView):

    def get(self, request, post_id):
        post = content_marketing_service.get_post_by_id_or_404(request.user, post_id)
        serializer = DetailPostSerializer(post, context={'request': request})
        return ok(serializer.data)

    def delete(self, request, post_id):
        post = content_marketing_service.get_post_by_id_or_404(request.user, post_id)
        post.delete()
        return no_content()


class PostCommentListApiView(BaseListAPIView):

    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return content_marketing_service.get_post_comments_by_post_id_or_404(self.request.user, post_id)


class ContentMarketingSettingsCreateUpdateRetrieveAPIView(RetrieveAPIView, UpdateModelMixin):

    serializer_class = ContentMarketingCreateRetrieveSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_object(self):
        if not hasattr(self.request.user, 'content_marketing_settings'):
            return None
        return self.request.user.content_marketing_settings

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

