from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request


class HasSMSPanelPermission(permissions.BasePermission):

    """
    Checks that user has access right to all smspanel views
    """

    message = "مدت استفاده از سرویس مورد نظر به اتمام رسیده یا اجازه دسترسی به آن را ندارید"

    def has_permission(self, request: Request, view: View):

        user = request.user

        try:
            user.businessmanmodulus_set.get(module__name='SMS', expire_at__gt=datetime.now())
        except ObjectDoesNotExist:
            return False

        return True
