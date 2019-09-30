from django.shortcuts import render

from rest_framework import generics, mixins, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from users.models import Customer
from .serializers import CustomerSerializer, CustomerListCreateSerializer



class BusinessmanCustomerListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    """
    get:
    NEW (pagination added) -  Generates a list of all customers that belongs to specific user. Needs JWT Token

    post:
    NEW (full name) is added- Registers a new customer for specific user. Needs JWT token
    """

    serializer_class = CustomerListCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        user            = self.request.user
        # customers_all   = Customer.objects.all()
        phone           = self.request.query_params.get('phone', None)
        full_name       = self.request.query_params.get('full_name', None)


        if (full_name and phone) is not None:
            Customer_list    = user.customers.filter(full_name__icontains=full_name,phone__icontains=phone)
            return Customer_list
        if full_name is not None:
            Customer_list    = user.customers.filter(full_name__icontains=full_name)
            return Customer_list
        if phone is not None:
            Customer_list    = user.customers.filter(phone__icontains=phone)
            return Customer_list


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
