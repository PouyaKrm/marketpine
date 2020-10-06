from django.utils import timezone
from django.conf import settings
from rest_framework import permissions
from rest_framework.request import Request

days_before_expire = settings.ACTIVATION_ALLOW_REFRESH_DAYS_BEFORE_EXPIRE


class ActivatePanelPermission(permissions.BasePermission):

    message = 'موعد فعال سازی مجدد پنل نرسیده است'

    def has_permission(self, request: Request, view):

        return request.user.can_activate_panel()

