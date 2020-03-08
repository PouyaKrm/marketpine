from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from smspanel.permissions import HasActiveSMSPanel, HasValidCreditSendSMSToAll


class HASFestivalAccess(permissions.BasePermission):

    message = "مدت استفاده از سرویس موردنظر به اتمام رسیده یا اجازه دسترسی به آن را ندارید"

    def has_permission(self, request: Request, view: View):

        try:
            request.user.businessmanmodulus_set.get(module__name='Festival', expire_at__gt=datetime.now())
        except ObjectDoesNotExist:
            return False

        return True
