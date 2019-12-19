from django.shortcuts import render
from .models import Post,Like,Comment
from .forms import PostForm
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from users.models import Customer

from .serializers import (UploadPostSerializer,DetailPostSerializer,
                         DetailCommentSerializer,DetailLikeSerializer,
                         SetCommentSerializer,SetLikeSerializer,
                         )

# class LikeView(APIView):
#     def post(self, request, *args, **kwargs):
#         # user = request.user
#         post_id = request.POST['post_id']
#         post = Post.objects.get(id=post_id)
#         like, created = Like.objects.get_or_create(post=post, user=customer)
#         return JsonResponse({"created": created})

@api_view(['POST'])
def set_comment_post(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    customer = get_object_or_404(Customer,phone = request.data['phone'])
    serializer = SetCommentSerializer(data=request.data,context={'post': post,'customer':customer})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def set_like_post(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    customer = get_object_or_404(Customer,phone = request.data['phone'])

    serializer = SetLikeSerializer(data=request.data,context={'post': post,'customer':customer})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def detail_comment_post(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    comments = post.comments.all()
    serializer = DetailCommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def detail_like_post(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    likes = post.likes.all()
    serializer = DetailLikeSerializer(likes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def detailpost(request, post_id):
    post = get_object_or_404(Post,pk=post_id)
    serializer = DetailPostSerializer(post)
    return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def like_create_api(request, video_id):
#     video = get_object_or_404(pk=video_id)
#     video.likers.add(request.user)
#     serializer = PhotoSerializer(photo)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

##TODO:set context with standard way
class PostUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):

        serializer = UploadPostSerializer(data=request.data)

        serializer._context = {'request': self.request}

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# def showpost(request):
#     lastpost= Post.objects.last()
#     videofile= lastpost.videofile
#     form= VideoForm(request.POST or None, request.FILES or None)
#     if form.is_valid():
#         form.save()
#
#     context= {'videofile': videofile,
#               'form': form,
#               'MEDIA_URL':settings.MEDIA_URL,
#               }
#     return render(request, 'content_marketing/videos.html', context)
