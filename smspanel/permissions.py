from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from django.conf import settings

from panelprofile.services import sms_panel_info_service
from smspanel.models import SMSMessage

english_sms_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']
send_plain_max_customers = settings.SMS_PANEL['SEND_PLAIN_CUSTOMERS_MAX_NUMBER']
min_credit = settings.SMS_PANEL['MIN_CREDIT']

from panelprofile.models import SMSPanelStatus


def check_has_min_credit(smsapnelinfo) -> bool:
    return smsapnelinfo.credit >= min_credit


def remained_credit_for_message(smspanelinfo) -> int:
    return smspanelinfo.remained_credit_for_new_message()


class HasActiveSMSPanel(permissions.BasePermission):

    message = 'پنل پیامک شما فعال نیست'

    def has_permission(self, request: Request, view: View):

        if request.method == 'GET':
            return True

        return sms_panel_info_service.fetch_panel_and_check_is_active(request.user)


class HasValidCreditSendSMSToInviduals(permissions.BasePermission):

    """
    Checks that businessman has enough credit for sending sms to specific amount of customers.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار شما برای ارسال پیام کافی نیست'

    def has_permission(self, request: Request, view: View):
        return sms_panel_info_service.get_panel_has_valid_credit_send_sms_inviduals(request.user)


class HasValidCreditSendSMSToAll(permissions.BasePermission):

    """
    Check that businessman has enough credit to send sms to all of his customers.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار شما برای ارسال پیام کافی نیست'

    def has_permission(self, request: Request, view: View):
        return sms_panel_info_service.get_panel_has_credit_for_message_to_all(request.user)


class HasValidCreditSendSMSToGroup(permissions.BasePermission):

    """
    Check that businessman has enough credit to send sms to all customers
    that belongs to a group if group exists.
    Use this Permission after IsAuthenticated Permission
    """
    message = "اعتبار کافی برای ارسال پیام موجود نیست"

    def has_permission(self, request: Request, view: View):
        try:
            group = request.user.businessmangroups_set.get(id=view.kwargs['group_id'])
        except ObjectDoesNotExist:
            return True
        return sms_panel_info_service.get_panel_has_valid_credit_send_to_group(request.user, group)


class HasValidCreditResendFailedSMS(permissions.BasePermission):

    message = 'اعتبار کافی برای باز ارسال پیام موجود نیست'

    def has_permission(self, request: Request, view: View):
        try:
            failed_sms = request.user.smsmessage_set.get(id=view.kwargs['sms_id'], status=SMSMessage.STATUS_FAILED)
        except ObjectDoesNotExist:
            return True

        return sms_panel_info_service.get_panel_has_valid_credit_resend_failed_sms(request.user, failed_sms)


class HasValidCreditResendTemplateSMS(permissions.BasePermission):

    """
    Check that businessman has enough credit to resend a template sms to all customers that has not received
    it if the record exists.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار کافی برای باز ارسال پیام موجود نیست'

    def has_permission(self, request: Request, view: View):
        try:
            unsent_sms = request.user.unsenttemplatesms_set.get(id=view.kwargs['unsent_sms_id'])
        except ObjectDoesNotExist:
            return True
        
        return sms_panel_info_service.get_panel_has_valid_credit_resend_template_sms(request.user, unsent_sms)

