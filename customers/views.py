from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.pginations import BasePageNumberPagination
from common.util.http_helpers import no_content, bad_request, ok
from .serializers import CustomerSerializer, CustomerListCreateSerializer
from .services import customer_service


class BusinessmanCustomerListAPIView(APIView):
    """
    get:
    NEW (pagination added) -  Generates a list of all customers that belongs to specific user. Needs JWT Token

    post:
    NEW (full name) is added- Registers a new customer for specific user. Needs JWT token
    """

    serializer_class = CustomerListCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        sr = CustomerListCreateSerializer(data=request.data, context=self.get_serializer_context())
        if not sr.is_valid():
            return bad_request(sr.errors)

        c = customer_service.add_customer(
            request.user, sr.validated_data.get('phone'),
            sr.validated_data.get('full_name'),
            sr.validated_data.get('groups'),
            purchase_price=sr.validated_data.get('purchase_price')
        )

        sr = CustomerListCreateSerializer(c, context=self.get_serializer_context())
        return ok(sr.data)

    def get(self, request: Request):
        paginator = BasePageNumberPagination()
        query_set = self.get_queryset()
        result = paginator.paginate_queryset(query_set, request)
        sr = CustomerListCreateSerializer(result, many=True, context=self.get_serializer_context())
        return paginator.get_paginated_response(sr.data)

    def get_queryset(self):
        user = self.request.user
        phone = self.request.query_params.get('phone', None)
        full_name = self.request.query_params.get('full_name', None)
        group_id = self.request.query_params.get('group_id', None)
        query = customer_service.get_businessman_customers(user)

        if phone is not None and type(phone) == str:
            query = query.filter(phone__icontains=phone)
        if full_name is not None and type(full_name) == str:
            query = query.filter(full_name__icontains=full_name)
        try:
            if group_id is None:
                return query.all()
            group_id = int(group_id)
            if group_id > 0:
                query = query.filter(membership__group__id=group_id,
                                     membership__group__businessman=user).order_by('-membership__create_date')
        except ValueError:
            pass

        return query.order_by('-membership__create_date').all()

    def get_serializer_context(self):
        g_id = self.request.query_params.get('is_group_member')
        context = {'user': self.request.user}
        if g_id is None:
            return context
        try:
            g_id = int(g_id)
            if g_id > 0:
                context['check_member_group_id'] = g_id
            return context
        except ValueError:
            return context


class BusinessmanCustomerRetrieveAPIView(APIView):
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

    def get(self, request: Request, customer_id: int):
        c = customer_service.get_businessman_customer_by_id(request.user, customer_id)
        sr = CustomerSerializer(c, context=self.get_serializer_context())
        return ok(sr.data)

    def get_object(self):
        c_id = self.kwargs.get('id')
        c = customer_service.get_customer_by_id_or_404(self.request.user, c_id)
        return c

    def put(self, request: Request, customer_id):
        sr = CustomerSerializer(data=request.data, context=self.get_serializer_context())
        if not sr.is_valid():
            return bad_request(sr.errors)

        c = customer_service.edit_customer_phone_full_name(
            request.user,
            customer_id,
            sr.validated_data.get('phone'),
            sr.validated_data.get('full_name')
        )
        sr = CustomerSerializer(c, context=self.get_serializer_context())
        return ok(sr.data)

    def delete(self, request, customer_id):
        c = customer_service.delete_customer_for_businessman(request.user, customer_id)
        sr = CustomerSerializer(c, context=self.get_serializer_context())
        return ok(sr.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        customer_service.delete_customer_for_businessman(request.user, kwargs.get('id'))
        return no_content()
