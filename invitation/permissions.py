from django.utils import timezone
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request


class HasInvitationAccess(permissions.BasePermission):

    message = 'تاریخ استفاده شما از دعوت دوستان به اتمام رسیده یا اجازه دسرسی به آن را ندارید'

    def has_permission(self, request: Request, view: View):

        # expired = request.user.friend_invitation_access_expire <= timezone.now()
        # return not expired
        return True
