from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from django.conf import settings

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

        return request.user.has_sms_panel and (request.user.smspanelinfo.status == SMSPanelStatus.ACTIVE_LOGIN)


class HasValidCreditSendSMS(permissions.BasePermission):

    """
    Checks that businessman has enough credit for sending sms to specific amount of customers.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار شما برای ارسال پیام کافی نیست'

    def has_permission(self, request: Request, view: View):
        smspanelinfo = request.user.smspanelinfo
        if (check_has_min_credit(smspanelinfo) and remained_credit_for_message(smspanelinfo) >
                send_plain_max_customers * english_sms_cost):
            return True
        return False


class HasValidCreditSendSMSToAll(permissions.BasePermission):

    """
    Check that businessman has enough credit to send sms to all of his customers.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار شما برای ارسال پیام کافی نیست'

    def has_permission(self, request: Request, view: View):

        smspanelinfo = request.user.smspanelinfo
        return check_has_min_credit(smspanelinfo) and smspanelinfo.has_remained_credit_for_new_message_to_all()



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
        
        return group.customers.count() * english_sms_cost < remained_credit_for_message(request.user.smspanelinfo)


class HasValidCreditResendFailedSMS(permissions.BasePermission):

    message = 'اعتبار کافی برای باز ارسال پیام موجود نیست'

    def has_permission(self, request: Request, view: View):

        smspanelinfo = request.user.smspanelinfo
        try:
            failed_sms = request.user.smsmessage_set.get(id=view.kwargs['sms_id'], status=SMSMessage.STATUS_FAILED)
        except ObjectDoesNotExist:
            return True

        return (remained_credit_for_message(smspanelinfo) and
                failed_sms.receivers.count() * english_sms_cost < remained_credit_for_message(smspanelinfo))


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
        
        return unsent_sms.customers.count() * english_sms_cost < request.user.smspanelinfo.credit
