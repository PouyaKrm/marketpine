from django.db.models import QuerySet
from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, generics, parsers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.http_helpers import bad_request, ok
from .models import MobileAppHeader, MobileAppPageConf
from .serializers import MobileAppHeaderSerializer, MobileAppPageConfSerializer, \
    MobileAppHeaderSerializer
from .services import mobile_page_conf_service


class MobileAppPageConfAPIView(APIView):

    def put(self, request):
        serializer = MobileAppPageConfSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return bad_request(serializer.errors)

        conf = mobile_page_conf_service.update_page_conf(request.user, serializer.validated_data)
        serializer = MobileAppPageConfSerializer(conf, context={'conf': conf, 'request': request})
        return ok(serializer.data)

    def get(self, request):
        conf = mobile_page_conf_service.get_businessman_conf_or_create(request.user)
        s = MobileAppPageConfSerializer(conf, context={'conf': conf, 'request': request})
        return ok(s.data)


@api_view(['POST'])
@parser_classes([parsers.MultiPartParser])
def upload_header_image(request: Request):
    serializer = MobileAppHeaderSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return bad_request(serializer.errors)
    return ok(serializer.create(serializer.validated_data))


class MobileAppHeaderDeleteAPIView(generics.DestroyAPIView):

    lookup_field = 'id'

    def get_queryset(self) -> QuerySet:
        return mobile_page_conf_service.get_businessman_all_app_headers(self.request.user)
