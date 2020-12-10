from datetime import timedelta, datetime
from django.db.models.expressions import F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.views import APIView

from common.util.http_helpers import ok
from dashboard.serializers import DashboardSerializer


class DashboardAPIView(APIView):

    def get(self, request):

        sr = DashboardSerializer(request.user, request=request)
        return ok(sr.data)
