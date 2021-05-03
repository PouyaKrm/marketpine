from base64 import b64decode
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
import jwt.exceptions as jwtEx
from rest_framework import permissions
from rest_framework.request import Request
import jwt
from django.conf import settings
from common.util import get_client_ip
from .models import BusinessmanRefreshTokens, Businessman


class HasValidRefreshToken(permissions.BasePermission):


    """
    Check if refresh token is presented in header and is valid.
    """

    message = "Refresh token is changed or is expired"

    def has_permission(self, request: Request, view: View):

        refresh_token = request.META.get('HTTP_X_API_KEY')

        if refresh_token is None:
            return False

        try:
            payload = jwt.decode(refresh_token, settings.REFRESH_KEY_PU, algorithms='RS256')
        except jwtEx.PyJWTError:
            return False

        ip = get_client_ip(request)

        try:
            BusinessmanRefreshTokens.objects.get(pk=payload['id'], username=payload['iss'],  ip=ip)
        except ObjectDoesNotExist:
            return False

        request.data['username'] = payload['iss']

        return True


class IsBusinessmanAuthorized(permissions.BasePermission):

    message = 'تا ارسال مدارک احراز هویت امکان دسترسی به این قسمت نیست'

    def has_permission(self, request: Request, view: View) -> bool:

        return request.user.is_authorized()


class IsPanelActive(permissions.BasePermission):

    message = 'تا فعال سازی پنل امکان دسترسی به این قسمت نیست'

    def has_permission(self, request: Request, view: View) -> bool:

        return request.user.is_panel_active()


class IsPanelActivePermissionPostPutMethod(IsPanelActive):

    def has_permission(self, request: Request, view) -> bool:
        if request.method != 'POST' and request.method != 'PUT':
            return True

        return super().has_permission(request, view)


class IsPhoneVerified(permissions.BasePermission):

    def has_permission(self, request: Request, view: View) -> bool:
        return request.user.is_phone_verified
