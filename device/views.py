from django.http import HttpResponse,HttpResponseRedirect
from .models import Device
from .serializers import CustomerRegisterSerializer
from django.http import JsonResponse
from users.models import Businessman,Customer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin





def register_customer(request,imei_number,phone_customer):
    if Device.objects.filter(imei=imei_number).exists():
        this_businessman=Businessman.objects.get(device__imei=imei_number)

        if not Customer.objects.filter(phone=phone_customer,businessman=this_businessman).exists():
            this_customer = Customer.objects.create(businessman=this_businessman,
                                                    phone=phone_customer,
                                                    full_name="test",
                                                    )

            get_id=this_customer.id
            return HttpResponse("customer_id:"+str(get_id))

        else:
            return HttpResponse("this customer already existed")

    else:
        return HttpResponse("FALSE:businessman dont exist")


class RegisterCustomer(GenericAPIView,CreateModelMixin):
    serializer_class=CustomerRegisterSerializer
