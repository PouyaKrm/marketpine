from django.utils import timezone
from django.conf import settings
from rest_framework import permissions
from rest_framework.request import Request

days_before_expire = settings.ACTIVATION_ALLOW_REFRESH_DAYS_BEFORE_EXPIRE


class ActivatePanelPermission(permissions.BasePermission):

    message = 'موعد فعال سازی مجدد پنل نرسیده است'

    def has_permission(self, request: Request, view):

        expire_date = request.user.panel_expiration_date

        if request.user.is_duration_permanent():
            return False

        if expire_date is None:
            return True

        now = timezone.now()
        return expire_date <= now or expire_date - now <= days_before_expire

