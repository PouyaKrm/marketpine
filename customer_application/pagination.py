from rest_framework.pagination import PageNumberPagination
from django.conf import settings

default_page_size = settings.CUSTOMER_APP_PAGINATION_SETTINGS['DEFAULT_PAGE_SIZE']
max_size = settings.CUSTOMER_APP_PAGINATION_SETTINGS['MAX_PAGE_SIZE']
query_param = settings.CUSTOMER_APP_PAGINATION_SETTINGS['PAGE_SIZE_QUERY_PARAM']


class CustomerAppListPaginator(PageNumberPagination):

    page_size = default_page_size
    page_size_query_param = query_param
    max_page_size = max_size

