from rest_framework import generics
from .pginations import BasePageNumberPagination


class BaseListAPIView(generics.ListAPIView):

    pagination_class = BasePageNumberPagination
