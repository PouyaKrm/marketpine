from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request
from smspanel.permissions import HasValidCreditSendSMSToAll

from .models import PostConfirmationStatus


class DoesNotHavePendingPostForUpload(permissions.BasePermission):

    message = 'شما یک محتوای منتظر تایید دارید و نمی توانید محتوای دیگری ارسال کنید'

    def has_permission(self, request: Request, view: View):
        # if request.method != 'POST':
        return True
        return not request.user.post_set.filter(confirmation_status=PostConfirmationStatus.PENDING).exists()


class HasValidCreditForVideoUploadMessage(permissions.BasePermission):

    message = 'اعتبار شما برای ارسال پیام مربوط به محتوای ارسال شده کافی نیست'

    def has_permission(self, request: Request, view: View):
        # user = request.user
        # if not hasattr(user, 'content_marketing_settings') or not user.content_marketing_settings.content_marketing_message:
        #     return True
        #
        # sms_permission = HasValidCreditSendSMSToAll()
        # return sms_permission.has_permission(request, view)

        return True


