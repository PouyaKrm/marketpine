from rest_framework import serializers
from .models import Device
from users.models import Businessman,Customer
from django.core.exceptions import ObjectDoesNotExist


class CustomerRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = [
            'id',

        ]
        extra_kwargs = {'id': {'read_only': True}}


    def validate(self, validate_data):
        imei_number=self.context['imei_number']
        phone_customer=self.context['phone_customer']


        if Device.objects.filter(imei=imei_number).exists():
            this_businessman=Businessman.objects.get(device__imei=imei_number)

            if  Customer.objects.filter(phone=phone_customer,businessman=this_businessman).exists():

                raise serializers.ValidationError({'customer': ['customer is existed already']})

            return validate_data
        else:
            raise serializers.ValidationError({'device': ['customer is not exist']})


    def create(self, validated_data):
        imei_number=self.context['imei_number']
        phone_customer=self.context['phone_customer']

        this_businessman=Businessman.objects.get(device__imei=imei_number)
        return Customer.objects.create(businessman=this_businessman,
                                      phone=phone_customer,
                                      **validated_data,
                                      )
