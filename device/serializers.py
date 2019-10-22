from rest_framework import serializers
from .models import Device


class CustomerRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = [
            'id',
            'imei',
        ]
        extra_kwargs = {'id': {'read_only': True},
                        'imei': {'required': True},
                       }

    def create(self, validated_data):
        request=self.context['request']
        return Device.objects.create(businessman=this_businessman,
                                     phone=this
                                      **validated_data,
                                      )
