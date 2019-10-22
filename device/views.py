from django.http import HttpResponse,HttpResponseRedirect
from .models import Device
from .serializers import CustomerRegisterSerializer
from django.http import JsonResponse
from users.models import Businessman,Customer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
def register_customer(request,imei_number,phone_customer):
    """
    Registers new customer. It Needs to be sended phone by url
    """

    serializer = CustomerRegisterSerializer(data=request.data,context={
                                            "imei_number":imei_number,
                                            "phone_customer":phone_customer,
                                            })

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer = serializer.save()

    return Response(data={'id': customer.id}, status=status.HTTP_201_CREATED)



#
# def register_customer(request,imei_number,phone_customer):
#     if Device.objects.filter(imei=imei_number).exists():
#         this_businessman=Businessman.objects.get(device__imei=imei_number)
#
#         if not Customer.objects.filter(phone=phone_customer,businessman=this_businessman).exists():
#             this_customer = Customer.objects.create(businessman=this_businessman,
#                                                     phone=phone_customer,
#                                                     full_name="test",
#                                                     )
#
#             get_id=this_customer.id
#             return HttpResponse("customer_id:"+str(get_id))
#
#         else:
#             return HttpResponse("this customer already existed")
#
#     else:
#         return HttpResponse("FALSE:businessman dont exist")



# 
# class RegisterCustomer(GenericAPIView,CreateModelMixin):
#     serializer_class=CustomerRegisterSerializer
#     def get_serializer_context(self):
#         context={
#                 "request":request,
#                 "imei_number":imei_number,
#                 "phone_customer":phone_customer,
#         }
#         return context
