from django.http import HttpResponse,HttpResponseRedirect
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


# GenericAPIView,CreateModelMixin
class RegisterCustomer(CreateAPIView):
    serializer_class = CustomerRegisterSerializer
    queryset = Customer.objects.all()


    def get_serializer_context(self):
        context={
                "imei_number":self.kwargs["imei_number"],
        }
        return context

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
