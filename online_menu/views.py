from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from common.util import create_detail_error
from common.util.http_helpers import no_content, bad_request, ok, not_found
from users.models import Businessman
from .serializers import OnlineMenuSerializer
from .models import OnlineMenu

# Create your views here.


class OnlineMenuAPIView(APIView):
    pagination_class = MultiPartParser

    def post(self, request):
        context = {'request': request}
        serializer = OnlineMenuSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return bad_request(serializer.errors)
        menu = serializer.create(serializer.validated_data)
        return ok(OnlineMenuSerializer(menu, context=context).data)

    def delete(self, request):
        result = OnlineMenu.delete_menu_for_user_if_exists(request.user)
        if result:
            return no_content()
        return not_found(create_detail_error('user has no online menu'))

    def put(self, request):
        return self.post(request)

    def get(self, request):
        obj = get_object_or_404(OnlineMenu, businessman=request.user)
        serializer = OnlineMenuSerializer(obj, context={'request': request})
        return ok(serializer.data)
