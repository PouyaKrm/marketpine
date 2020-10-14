from django.conf import settings
from rest_framework.pagination import PageNumberPagination

page_size = settings.PAGINATION_PAGE_NUM


class BasePageNumberPagination(PageNumberPagination):
    page_size = page_size
    page_size_query_param = 'page_size'
    max_page_size = 100
