from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.request import Request

from django.conf import settings


english_sms_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']
send_plain_max_customers = settings.SMS_PANEL['SEND_PLAIN_CUSTOMERS_MAX_NUMBER']
max_allowed_defined_templates = settings.SMS_PANEL['MAX_ALLOWED_DEFINED_TEMPLATES']


class HasValidDefinedTemplates(permissions.BasePermission):

    """
    Checks that maximum number of defined sms templates is not reached.
    """

    message = f"حداکثر تعددا مجاز قالب ها {max_allowed_defined_templates} است، که شما به آن رسیده اید"

    def has_permission(self, request: Request, view: View):
        return request.user.smstemplate_set.all().count() < max_allowed_defined_templates


class HasValidCreditSendSMS(permissions.BasePermission):

    """
    Checks that businessman has enough credit for sending sms to specific amount of customers.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار شما برای ارسال پیام کافی نیست'

    def has_permission(self, request: Request, view: View):

        return request.user.smspanelinfo.credit > send_plain_max_customers * english_sms_cost


class HasValidCreditSendSMSToAll(permissions.BasePermission):

    """
    Check that businessman has enough credit to send sms to all of his customers.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار شما برای ارسال پیام کافی نیست'

    def has_permission(self, request: Request, view: View):

        return request.user.smspanelinfo.credit > request.user.customers.count() * english_sms_cost


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
        
        return group.customers.count() * english_sms_cost < request.user.smspanelinfo.credit

class HasValidCreditResendPlainSMS(permissions.BasePermission):

    """
    Check that businessman has enough credit to resend a plain sms to all customers that has not received
    it if the record exists.
    Use this Permission after IsAuthenticated Permission
    """

    message = 'اعتبار کافی برای باز ارسال پیام موجود نیست'

    def has_permission(self, request: Request, view: View):

        try:
            unsent_sms = request.user.unsentplainsms_set.get(id=view.kwargs['unsent_sms_id'])
        except ObjectDoesNotExist:
            return True

        return unsent_sms.customers.count() * english_sms_cost < request.user.smspanelinfo.credit


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
