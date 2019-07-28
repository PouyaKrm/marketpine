from django.db.models import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.serializers import Serializer


class NumberedPaginator(PageNumberPagination):

    def __init__(self, request: Request, query_set: QuerySet, srl: Serializer.__class__, page_size_value: int = 10):

        self.srl = srl
        self.query_set = query_set
        self.request = request
        self.page_size = page_size_value

    def next_page(self):

        page_result = self.paginate_queryset(self.query_set, self.request)
        serializer = self.srl(page_result, many=True)

        return self.get_paginated_response(serializer.data)
