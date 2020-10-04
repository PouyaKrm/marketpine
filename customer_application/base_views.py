from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.views import APIView

from common.util.http_helpers import get_user_agent
from customer_application.exceptions import CustomerServiceException
from customer_application.pagination import CustomerAppListPaginator
from customer_application.services import customer_auth_service


class CustomerAuthenticationSchema(BaseAuthentication):

    def authenticate(self, request: Request):

        err = exceptions.AuthenticationFailed('No such user')
        anonymous = AnonymousUser()

        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None or token.strip() == '':
            return anonymous, None
        user_agent = get_user_agent(request)

        try:
            return customer_auth_service.get_customer_by_login_token(token, user_agent), None
        except CustomerServiceException:
            return anonymous, None

    def authenticate_header(self, request: Request):
        return 'invalid token'


class BaseAPIView(APIView):

    authentication_classes = [CustomerAuthenticationSchema]


class BaseListAPIView(ListAPIView):

    authentication_classes = [CustomerAuthenticationSchema]
    pagination_class = CustomerAppListPaginator

    def get_serializer_context(self):
        return {'request': self.request}


class BaseRetrieveAPIView(RetrieveAPIView):

    authentication_classes = [CustomerAuthenticationSchema]

    def get_serializer_context(self):
        return {'request': self.request}
