from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.util import create_detail_error
from common.util.http_helpers import no_content, bad_request, ok, not_found
from common.util.sms_panel.message import SystemSMSMessage
from users.models import Businessman
from .serializers import OnlineMenuSerializer
from .models import OnlineMenu

# Create your views here.
from .services import online_menu_service


class OnlineMenuAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = OnlineMenuSerializer(data=request.data, request=request)
        if not serializer.is_valid():
            return bad_request(serializer.errors)
        menu = online_menu_service.add_image(request.user, serializer.validated_data.get('image'),
                                             serializer.validated_data.get('show_order'),
                                             serializer.validated_data.get('new_show_orders'))
        if not menu[0]:
            return bad_request(create_detail_error('max allowed headers reached'))
        return ok(OnlineMenuSerializer(menu[1], request=request).data)

    def get(self, request):
        menus = online_menu_service.get_all_menus(request.user)
        serializer = OnlineMenuSerializer(menus, many=True, context={'request': request})
        return ok(serializer.data)


class OnlineMenuRetrieveDeleteAPIView(APIView):

    def get(self, request: Request, menu_id: int):
        m = online_menu_service.get_menu_by_id(request.user, menu_id)
        if m is None:
            return not_found()
        sr = OnlineMenuSerializer(m, request=request)
        return ok(sr.data)

    def delete(self, request: Request, menu_id: int):
        result = online_menu_service.delete_menu_by_id(request.user, menu_id)
        if result is not None:
            sr = OnlineMenuSerializer(result, request=request)
            return ok(sr.data)
        return not_found(create_detail_error('user has no online menu'))
