from django.shortcuts import render
from .models import Video
from .forms import VideoForm
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import VideoSerializer


def showvideo(request):

    lastvideo= Video.objects.last()
    videofile= lastvideo.videofile

    form= VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()


    context= {'videofile': videofile,
              'form': form,
              'MEDIA_URL':settings.MEDIA_URL,
              }

    return render(request, 'content_marketing/videos.html', context)




class VideoUploadView(APIView):
    parser_class = (FileUploadParser,)
    
    def post(self, request):

        serializer = VideoSerializer(data=request.data)

        serializer._context = {'request': self.request}

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
