from django.db.models import QuerySet
from django.http.request import HttpRequest
from rest_framework import pagination
from rest_framework.request import Request

from panelprofile.models import SMSPanelInfo
from django.conf import settings


class SentSMSNumberedPaginator(pagination.PageNumberPagination):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self

    def paginate_queryset(self, queryset: QuerySet, request: Request, view=...):
        self.user = request.user
        page_size = self.get_page_size(request)
        if queryset.co


    def get_paginated_response(self, data):

        api_key = SMSPanelInfo.get_businessman_api_key(self.re)


class CustomPaginationSerializer(pagination.BasePaginationSerializer)
