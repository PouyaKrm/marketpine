from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum

from base_app.error_codes import ApplicationErrorCodes
from groups.models import BusinessmanGroups
from smspanel.models import SMSMessage, WelcomeMessage, SentSMS, SMSTemplate, SMSMessageReceivers, \
    SMSMessageReceiverGroup
from users.models import Businessman


def get_failed_messages(*args, businessman: Businessman):
    return SMSMessage.objects.filter(businessman=businessman, status=SMSMessage.STATUS_FAILED).order_by('-create_date')


def get_welcome_message(*args, businessman: Businessman) -> WelcomeMessage:
    try:
        return WelcomeMessage.objects.get(businessman=businessman)
    except ObjectDoesNotExist:
        s = WelcomeMessage.objects.create(businessman=businessman,
                                          message='به {} خوش آمدید'.format(businessman.business_name))
        return s


def get_sent_sms(*args, businessman: Businessman, receptor_phone: str = None):
    q = SentSMS.objects.filter(sms_message__businessman=businessman).order_by('-create_date')
    if receptor_phone is None:
        return q
    return q.filter(receptor=receptor_phone)


def get_pending_messages(*args, businessman: Businessman):
    return SMSMessage.objects.filter(businessman=businessman, status=SMSMessage.STATUS_PENDING)


def get_sms_template_by_id(*args, businessman: Businessman, template_id: int,
                           error_field_name: str = None) -> SMSTemplate:
    try:
        return SMSTemplate.objects.get(businessman=businessman, id=template_id)
    except ObjectDoesNotExist as ex:
        if error_field_name is not None:
            raise ApplicationErrorCodes.get_field_error(error_field_name, ApplicationErrorCodes.RECORD_NOT_FOUND,
                                                        ex)
        else:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)


def get_reserved_credit_of_pending_messages(*args, businessman: Businessman) -> int:
    r = get_pending_messages(businessman=businessman).aggregate(Sum('reserved_credit'))['reserved_credit__sum']
    if r is None:
        return 0
    return r


def has_message_any_receivers(*args, sms_message: SMSMessage) -> bool:
    return SMSMessageReceivers.objects.filter(sms_message=sms_message, is_sent=False).exists()


def _get_message(
        *args,
        businessman: Businessman,
        sms_id: int,
        status: str = None,
        field_name: str = None) -> SMSMessage:
    if status is not None:
        try:
            return SMSMessage.objects.get(businessman=businessman, id=sms_id, status=status)
        except ObjectDoesNotExist as ex:
            if field_name is not None:
                raise ApplicationErrorCodes.get_field_error(field_name, ApplicationErrorCodes.RECORD_NOT_FOUND, ex)
            else:
                raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)
    else:
        try:
            return SMSMessage.objects.get(businessman=businessman, id=sms_id)
        except ObjectDoesNotExist as ex:
            if field_name is not None:
                raise ApplicationErrorCodes.get_field_error(field_name, ApplicationErrorCodes.RECORD_NOT_FOUND, ex)
            else:
                raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)


def get_sms_templates(*args, businessman: Businessman):
    return SMSTemplate.objects.filter(businessman=businessman).order_by('-create_date')


def get_receiver_group_member_count(*args, sms_message: SMSMessage) -> int:
    return SMSMessageReceiverGroup.objects.get(sms_message=sms_message).group.customers.count()


def get_sms_message_receivers(*args, sms_message: SMSMessage):
    return SMSMessageReceivers.objects.filter(sms_message=sms_message, is_sent=False)
