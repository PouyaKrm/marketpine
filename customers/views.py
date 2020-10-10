from django.shortcuts import render

from rest_framework import generics, mixins, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from common.util.http_helpers import no_content
from users.models import Customer
from .serializers import CustomerSerializer, CustomerListCreateSerializer
from .paginations import StandardResultsSetPagination
from .services import customer_service


class BusinessmanCustomerListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    """
    get:
    NEW (pagination added) -  Generates a list of all customers that belongs to specific user. Needs JWT Token

    post:
    NEW (full name) is added- Registers a new customer for specific user. Needs JWT token
    """

    serializer_class = CustomerListCreateSerializer
    pagination_class = StandardResultsSetPagination


    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        # customers_all   = Customer.objects.all()
        phone = self.request.query_params.get('phone', None)
        full_name = self.request.query_params.get('full_name', None)
        # query = user.customers.order_by('date_joined')
        query = customer_service.get_businessman_customers(user)
        if (full_name and phone) is not None:
            return query.filter(full_name__icontains=full_name, phone__icontains=phone)
        elif full_name is not None:
            return query.filter(full_name__icontains=full_name)
        elif phone is not None:
            return query.filter(phone__icontains=phone)
        else:
            return query.all()

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
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'user': self.request.user, 'customer_id': self.kwargs.get('id')}

    def get_object(self):

        c_id = self.kwargs.get('id')
        c = customer_service.get_customer_by_id_or_404(self.request.user, c_id)
        return c


    def put(self, request: Request, *args, **kwargs):

        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        customer_service.delete_customer_for_businessman(request.user, kwargs.get('pk'))
        return no_content()
