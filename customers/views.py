from django.shortcuts import render

from rest_framework import generics, mixins, permissions
from rest_framework.generics import  RetrieveAPIView


from .serializers import CustomerSerializer



class BusinessmanCustomerListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    """
    get:
    Generates a list of all customers that belongs to specific user. Needs JWT Token

    post:
    Registers a new customer for specific user. Needs JWT token
    """

    serializer_class = CustomerSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):

        return self.request.user.customers.all()

    def get_serializer_context(self):

        return {'user': self.request.user}



class BusinessmanCustomerRetrieveAPIView(mixins.DestroyModelMixin, RetrieveAPIView):

    """
    get:
    Retrieves a specific user by it's id. Needs JWT token.

    delete:
    Deletes specific customer. Needs JWT token.
    """

    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        return self.request.user.customers.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

