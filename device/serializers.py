from rest_framework import serializers
from .models import Device
from users.models import Businessman,Customer
from django.core.exceptions import ObjectDoesNotExist
from common.util.custom_validators import phone_validator


class CustomerRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=15,validators=[phone_validator])

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',

        ]
        extra_kwargs = {'id': {'read_only': True},
                        'phone':{'required':True}
                       }


    def validate(self, validate_data):
        imei_number = self.context['imei_number']
        phone = validate_data.get('phone')


        if Device.objects.filter(imei=imei_number).exists():
            this_businessman = Businessman.objects.get(device__imei=imei_number)

            if  Customer.objects.filter(phone= phone,businessman= this_businessman).exists():

                raise serializers.ValidationError({'customer': ['مشستری از قبل ثبت شده است']})

            return validate_data

        else:
            raise serializers.ValidationError({'device': ['device does not exist']})

    def create(self, validated_data):
        imei_number = self.context['imei_number']
        this_businessman = Businessman.objects.get(device__imei = imei_number)

        return Customer.objects.create(businessman = this_businessman,
                                       **validated_data,
                                      )
