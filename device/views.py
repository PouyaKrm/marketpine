from django.http import HttpResponse,HttpResponseRedirect
from rest_framework.views import APIView

from common.util.http_helpers import bad_request, ok
from invitation.serializers import BaseFriendInvitationSerializer
from .models import Device
from .serializers import CustomerRegisterSerializer
from django.http import JsonResponse
from users.models import Businessman,Customer
from common.util.custom_validators import phone_validator


from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView ,CreateAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.decorators import api_view, permission_classes

from .authentication import DeviceAuthenticationSchema


# GenericAPIView,CreateModelMixin

class BaseCreateAPIView(CreateAPIView):
    authentication_classes = [DeviceAuthenticationSchema]

    def get_serializer_context(self):
        return {'user': self.request.user}


class BaseAPIView(APIView):
    authentication_classes = [DeviceAuthenticationSchema]


class RegisterCustomer(BaseCreateAPIView):
    serializer_class = CustomerRegisterSerializer
    queryset = Customer.objects.all()


class InviteFriend(BaseAPIView):

    def post(self, request):

        serializer = BaseFriendInvitationSerializer(data=request.data, context={'user': request.user})
        if not serializer.is_valid():
            return bad_request(serializer.errors)

        return ok(serializer.create(serializer.validated_data))

# 
# @api_view(['POST'])
# def register_customer(request,imei_number):
#     """
#     Registers new customer. It Needs to be sended phone by url
#     """
#
#     serializer = CustomerRegisterSerializer(data=request.data,context={
#                                             "imei_number":imei_number,
#                                             })
#
#     if not serializer.is_valid():
#
#         return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
#
#     customer = serializer.save()
#
#     return Response(data={'id': customer.id}, status=status.HTTP_201_CREATED)
