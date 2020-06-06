from django.shortcuts import render

# Create your views here.
from rest_framework import permissions
from rest_framework.views import APIView

from common.util.http_helpers import bad_request, ok
from .permissions import HasAllowedToUploadMoreHeaderImage
from .serializers import MobileAppHeaderSerializer


class MobileAppPageConfAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated, HasAllowedToUploadMoreHeaderImage]

    def post(self, request):
        serializer = MobileAppHeaderSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return bad_request(serializer.errors)
        return ok(serializer.create(serializer.validated_data))

