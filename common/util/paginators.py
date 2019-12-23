from django.db.models import QuerySet
from django.conf import settings

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework import status

from common.util import create_link

page_page_size = settings.PAGINATION_PAGE_NUM

class PageNumberPaginationSize10(PageNumberPagination):
    page_size = page_page_size

class NumberedPaginator(PageNumberPagination):

    def __init__(self, request: Request, query_set: QuerySet, srl: Serializer.__class__, page_size_value: int = 25):

        self.srl = srl
        self.query_set = query_set
        self.request = request
        self.page_size = page_page_size

    def next_page(self):

        page_result = self.paginate_queryset(self.query_set, self.request)
        serializer = self.srl(page_result, many=True)

        return self.get_paginated_response(serializer.data)

def create_pagination_response(page, result: list, count: int, retrieve_link: str, request: Request):

    data = {}
    if page.has_next():
        data['next'] = retrieve_link + f"?page={page.next_page_number()}"
    else:
        data['next'] = None
    
    if page.has_previous():
        data['previous'] = retrieve_link + f"?page={page.previous_page_number()}"
    else:
        data['previous'] = None
    
    data['count'] = count

    data['result'] = result

    return Response(data, status=status.HTTP_200_OK)



    