from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from .models import Festival


class CanDeleteOrUpdateFestival(permissions.BasePermission):

    message = 'امکان حذف این پیام وجود ندارد'

    def has_object_permission(self, request: Request, view: View, obj: Festival):
        if obj.businessman != request.user:
            return False
        if request.method == 'DELETE':
            return obj.can_delete()
        if request.method == 'PUT':
            return obj.can_edit()
        return True


class HASFestivalAccess(permissions.BasePermission):

    message = "مدت استفاده از سرویس موردنظر به اتمام رسیده یا اجازه دسترسی به آن را ندارید"

    def has_permission(self, request: Request, view: View):

        try:
            request.user.businessmanmodulus_set.get(module__name='Festival', expire_at__gt=datetime.now())
        except ObjectDoesNotExist:
            return False

        return True
