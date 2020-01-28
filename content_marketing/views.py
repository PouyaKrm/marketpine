from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from .models import Post
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin
from django.shortcuts import get_object_or_404
from users.models import Customer

from .serializers import (UploadListPostSerializer, DetailPostSerializer,
                          CommentSerializer, DetailLikeSerializer,
                          SetCommentSerializer, SetLikeSerializer,
                          )

video_page_size = settings.UPLOAD_VIDEO['VIDEO_PAGINATION_PAGE_SIZE']


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
    post = get_object_or_404(Post,pk=post_id)
    comments = post.comments.all()
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def detail_like_post(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    likes = post.likes.all()
    serializer = DetailLikeSerializer(likes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class PostCreateListAPIView(CreateAPIView, ListModelMixin):
    parser_class = (FileUploadParser,)
    serializer_class = UploadListPostSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = video_page_size

    def get_queryset(self):
        return self.request.user.post_set.order_by('-creation_date').all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'request': self.request}


class PostRetrieveDeleteAPIView(APIView):

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = DetailPostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        try:
            request.user.post_set.get(id=post_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PostCommentListApiView(ListAPIView):

    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id, businessman=self.request.user)
            return post.comments.all()
        except ObjectDoesNotExist:
            raise NotFound()

