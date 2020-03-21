from django.core.exceptions import ObjectDoesNotExist
from rest_framework import authentication, exceptions
from rest_framework.request import Request
from .models import Device


class DeviceAuthenticationSchema(authentication.BaseAuthentication):

    def authenticate(self, request: Request):
        device_key = request.META.get('HTTP_X_DEVICE_KEY')

        if device_key is None:
            return None

        error = exceptions.AuthenticationFailed('device with provided key does not exist')
        try:
            device = Device.objects.get(key=device_key)
        except ObjectDoesNotExist:
            raise error

        if device.disabled:
            raise error

        return device.businessman, None

