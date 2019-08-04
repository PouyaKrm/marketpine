from django.shortcuts import render

from rest_framework import generics, mixins, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request

from .serializers import CustomerSerializer




class BusinessmanCustomerListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    """
    get:
    NEW (pagination added) -  Generates a list of all customers that belongs to specific user. Needs JWT Token

    post:
    NEW (full name) is added- Registers a new customer for specific user. Needs JWT token
    """

    serializer_class = CustomerSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):

        return self.request.user.customers.all()

    def get_serializer_context(self):

        return {'user': self.request.user}


class BusinessmanCustomerRetrieveAPIView(mixins.DestroyModelMixin, RetrieveAPIView, mixins.UpdateModelMixin):

    """
    get:
    Retrieves a specific user by it's id. Needs JWT token.

    delete:
    Deletes specific customer. Needs JWT token.
    """

    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_serializer_context(self):
        return {'user': self.request.user, 'customer_id': self.kwargs.get('pk')}

    def get_queryset(self):

        return self.request.user.customers.all()

    def put(self, request: Request, *args, **kwargs):

        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

