from django.shortcuts import render

from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveDestroyAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomerSerializer, SalesmenCustomerSerializer
from users.models import Customer, Salesman, SalesmenCustomer


class SalesmanCustomerListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    serializer_class = SalesmenCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):

        return SalesmenCustomer.objects.filter(salesman=self.request.user)

    def get_serializer_context(self):

        return {'request': self.request}


class SalesmanCustomerRetrieveAPIView(mixins.DestroyModelMixin, RetrieveAPIView):

    serializer_class = SalesmenCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        return SalesmenCustomer.objects.filter(salesman=self.request.user)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

