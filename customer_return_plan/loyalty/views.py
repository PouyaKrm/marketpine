from django.shortcuts import render

# Create your views here.
from rest_framework.request import Request
from rest_framework.views import APIView

from common.util.http_helpers import ok, bad_request
from .services import loyalty_service

from .serializers import LoyaltySettingsSerializer


class LoyaltySettingsRetrieveUpdateAPIVIew(APIView):

    def get(self, request: Request):
        obj = loyalty_service.get_businessman_loyalty_settings(request.user)
        serializer = LoyaltySettingsSerializer(obj)
        return ok(serializer.data)

    def put(self, request: Request):
        serializer = LoyaltySettingsSerializer(data=request.data)
        if not serializer.is_valid():
            return bad_request(serializer.errors)
        obj = loyalty_service.get_businessman_loyalty_settings(request.user)
        serializer = LoyaltySettingsSerializer(serializer.update(obj, serializer.validated_data))
        return ok(serializer.data)

