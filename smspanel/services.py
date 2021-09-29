from typing import List

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.db.models.aggregates import Sum

from base_app.error_codes import ApplicationErrorCodes
from common.util.kavenegar_local import APIException
from common.util.sms_panel.exceptions import SendSMSException
from common.util.sms_panel.helpers import calculate_total_sms_cost
from common.util.sms_panel.message import ClientBulkToAllToCustomerSMSMessage
from groups.models import BusinessmanGroups
from panelprofile.models import SMSPanelInfo
from users.models import Businessman, Customer
from .models import UnsentTemplateSMS, SentSMS, UnsentPlainSMS, SMSMessage, SMSMessageReceivers, WelcomeMessage, \
    SMSTemplate
from .selectors import get_welcome_message, _get_template_by_id, _get_message, has_message_any_receivers

max_message_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']


def send_template_sms_message_to_all(user: Businessman, template: str):
    """
    Because send to all by template does not have any serailizer, this helper method is created.
    This method send sms message to all customers and saves the record of them in the database.
    """

    client_sms = ClientBulkToAllToCustomerSMSMessage(user, template)

    try:
        sent_messages = client_sms.send_bulk()
    except SendSMSException as e:
        UnsentTemplateSMS(businessman=user, template=template, resend_start=e.failed_on.id)
        raise APIException(e.status, e.message)

    while sent_messages is not None:
        user.smspanelinfo.reduce_credit_local(calculate_total_sms_cost(sent_messages))
        SentSMS.objects.bulk_create(
            [SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
        try:
            sent_messages = client_sms.send_bulk()
        except SendSMSException as e:
            UnsentTemplateSMS(businessman=user, template=template, resend_start=e.failed_on.id)
            raise APIException(e.status, e.message)


class SMSMessageService:

    def create_unsent_plain_sms(self, ex: SendSMSException, content: str, user: Businessman, receptors: QuerySet):

        remained_recoptors = receptors.order_by('id').filter(id__gte=ex.failed_on.id).all()
        obj = UnsentPlainSMS.objects.create(businessman=user, message=content)
        obj.customers.add(*remained_recoptors)
        obj.save()

    def create_unsent_template_sms(self, ex: SendSMSException, template: str, businessman: Businessman,
                                   receptors: QuerySet):

        remained_receptors = receptors.order_by('id').filter(id__gte=ex.failed_on.id).all()
        obj = UnsentTemplateSMS.objects.create(businessman=businessman, template=template)
        obj.customers.add(*remained_receptors)
        obj.save()

    def __set_receivers_for_sms_message(self, sms: SMSMessage, customers: QuerySet):

        SMSMessageReceivers.objects.bulk_create(
            [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers.all()
             ])
        sms.save()
        sms.set_reserved_credit_by_receivers()

    def send_plain_sms(self, user: Businessman, customer_ids: List[int], message: str) -> SMSPanelInfo:
        from panelprofile.services import sms_panel_info_service
        from customers.services import customer_service
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        customers = customer_service.get_bsuinessman_customers_by_ids(user, customer_ids)
        if customers.count() == 0:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)
        sms = SMSMessage.objects.create(message=message, businessman=user, message_type=SMSMessage.TYPE_PLAIN,
                                        status=SMSMessage.STATUS_PENDING)
        SMSMessageReceivers.objects.bulk_create(
            [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers
             ])
        sms.save()
        sms.set_reserved_credit_by_receivers()
        return info

    def send_plain_sms_to_all(self, user: Businessman, message: str):
        from customers.services import customer_service
        from panelprofile.services import sms_panel_info_service
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        sms = SMSMessage.objects.create(message=message, businessman=user, message_type=SMSMessage.TYPE_PLAIN)
        SMSMessageReceivers.objects.bulk_create(
            [SMSMessageReceivers(sms_message=sms, customer=c) for c in
             customer_service.get_businessman_customers(user).all()
             ])
        sms.set_reserved_credit_by_receivers()
        return info

    def send_by_template(self,
                         user: Businessman, customer_ids: List[int],
                         template: int) -> SMSPanelInfo:

        from customers.services import customer_service
        from panelprofile.services import sms_panel_info_service
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        template = self._get_template_by_id(user, template, "template")
        customers = customer_service.get_bsuinessman_customers_by_ids(user, customer_ids)
        if customers.count() == 0:
            raise ApplicationErrorCodes.get_field_error("customers", ApplicationErrorCodes.RECORD_NOT_FOUND)
        self._send_by_template(user, customers, template.content, SMSMessage.USED_FOR_NONE)
        return info

    def send_by_template_to_all(self, user: Businessman, template: int) -> SMSPanelInfo:
        from panelprofile.services import sms_panel_info_service
        temp = self._get_template_by_id(user, template)
        sms = self._send_by_template_to_all(user, temp.content, SMSMessage.USED_FOR_NONE)
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        return info

    def send_plain_to_group(self, user: Businessman, group_id: int, message: str) -> SMSPanelInfo:
        from panelprofile.services import sms_panel_info_service
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        try:
            group = BusinessmanGroups.get_group_by_id(user, group_id)
            self._send_plain(user, group.get_all_customers(), message)
            return info
        except ObjectDoesNotExist as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)

    def send_by_template_to_group(self, user: Businessman, group_id: int, template_id: int) -> SMSPanelInfo:
        from panelprofile.services import sms_panel_info_service
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        template = self._get_template_by_id(user, template_id, "template_id")
        try:
            group = BusinessmanGroups.get_group_by_id(user, group_id)
        except ObjectDoesNotExist as ex:
            raise ApplicationErrorCodes.get_field_error("group_id", ApplicationErrorCodes.RECORD_NOT_FOUND, ex)

        self._send_by_template(user, group.get_all_customers(), template.content)
        return info

    def get_failed_messages(self, user: Businessman):
        return SMSMessage.objects.filter(businessman=user, status=SMSMessage.STATUS_FAILED).order_by('-create_date')

    def resend_failed_message(self, user: Businessman, sms_id: int) -> SMSPanelInfo:
        from panelprofile.services import sms_panel_info_service
        info = sms_panel_info_service.get_buinessman_sms_panel(user)
        sms = self._get_message(user, sms_id, SMSMessage.STATUS_FAILED)
        self.set_message_to_pending(sms)
        return info

    def set_message_to_pending(self, sms_messsage: SMSMessage):

        if not sms_messsage.has_any_unsent_receivers():
            sms_messsage.set_done()
        sms_messsage.reset_to_pending()
        return sms_messsage

    def update_not_pending_message_text(self, sms_message: SMSMessage, new_message: str):
        if sms_message.status == SMSMessage.STATUS_PENDING:
            raise ValueError('sms message most not be in pending mode for send')
        sms_message.message = new_message
        sms_message.save()

    def resend_unsent_template_sms(self, user: Businessman, unsent_sms: UnsentTemplateSMS):

        """

        """

        customers = unsent_sms.customers.all()
        UnsentTemplateSMS.objects.filter(id=unsent_sms.id).delete()
        try:
            self.send_by_template(user, customers, unsent_sms.template)
        except APIException as e:
            raise e

    def content_marketing_message_status_cancel(self, template: str, user: Businessman) -> SMSMessage:

        return self._send_by_template_to_all(user, template, SMSMessage.USED_FOR_CONTENT_MARKETING,
                                             status=SMSMessage.STATUS_CANCLE)

    def set_content_marketing_message_to_pending(self, sms_message):
        return self.set_message_to_pending(sms_message)

    def festival_message_status_cancel(self, template: str, user: Businessman) -> SMSMessage:
        return self._send_by_template_to_all(user, template, SMSMessage.USED_FOR_FESTIVAL,
                                             status=SMSMessage.STATUS_CANCLE)

    def friend_invitation_message(self, user: Businessman, template: str, customer):
        return self._send_by_template(user, [customer], template, SMSMessage.USED_FOR_FRIEND_INVITATION)

    def send_welcome_message(self, user: Businessman, customer) -> SMSMessage:
        wm = self.get_welcome_message_or_create(user)
        if not user.has_sms_panel or not wm.send_message:
            return None
        return self._send_by_template(user, [customer], wm.message, SMSMessage.USED_FOR_WELCOME_MESSAGE)

    def update_welcome_message(self, businessman: Businessman, message: str, send_message: bool) -> WelcomeMessage:
        w = self.get_welcome_message_or_create(businessman)
        w.message = message
        w.send_message = send_message
        w.save()
        return w

    def get_welcome_message_or_create(self, businessman: Businessman) -> WelcomeMessage:
        try:
            return WelcomeMessage.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            s = WelcomeMessage.objects.create(businessman=businessman,
                                              message='به {} خوش آمدید'.format(businessman.business_name))
            return s

    def get_sent_sms(self, businessman: Businessman, receptor_phone: str = None):
        q = SentSMS.objects.filter(sms_message__businessman=businessman).order_by('-create_date')
        if receptor_phone is None:
            return q
        return q.filter(receptor=receptor_phone)

    def get_pending_messages(self, user: Businessman):
        return SMSMessage.objects.filter(businessman=user, status=SMSMessage.STATUS_PENDING)

    def get_reserved_credit_of_pending_messages(self, user: Businessman) -> int:
        r = self.get_pending_messages(user).aggregate(Sum('reserved_credit'))['reserved_credit__sum']
        if r is None:
            return 0
        return r

    def _get_template_by_id(self, user: Businessman, template: int, error_field_name: str = None) -> SMSTemplate:
        try:
            return SMSTemplate.objects.get(businessman=user, id=template)
        except ObjectDoesNotExist as ex:
            if error_field_name is not None:
                raise ApplicationErrorCodes.get_field_error(error_field_name, ApplicationErrorCodes.RECORD_NOT_FOUND,
                                                            ex)
            else:
                raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)

    def _send_by_template_to_all(self, user: Businessman, template: str,
                                 used_for=SMSMessage.USED_FOR_NONE,
                                 **kwargs) -> SMSMessage:
        from customers.services import customer_service
        sms = SMSMessage.objects.create(message=template, businessman=user, used_for=used_for,
                                        message_type=SMSMessage.TYPE_TEMPLATE, **kwargs)
        self.__set_receivers_for_sms_message(sms, customer_service.get_businessman_customers(user))

        return sms

    def _send_by_template(self,
                          user: Businessman,
                          customers: QuerySet,
                          template: str,
                          used_for=SMSMessage.USED_FOR_NONE, **kwargs) -> SMSMessage:

        sms = SMSMessage.objects.create(
            message=template,
            businessman=user,
            message_type=SMSMessage.TYPE_TEMPLATE,
            used_for=used_for, **kwargs)
        SMSMessageReceivers.objects.bulk_create(
            [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers]
        )
        sms.set_reserved_credit_by_receivers()
        return sms

    def _send_plain(self, user: Businessman, customers: QuerySet, message: str,
                    used_for: str = SMSMessage.USED_FOR_NONE, **kwargs) -> SMSMessage:
        sms = SMSMessage.objects.create(
            message=message,
            businessman=user,
            message_type=SMSMessage.TYPE_PLAIN,
            used_for=used_for, **kwargs)
        SMSMessageReceivers.objects.bulk_create(
            [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers]
        )
        sms.set_reserved_credit_by_receivers()
        return sms

    def _get_message(self, user: Businessman, sms_id: int, status: str = None, field_name: str = None) -> SMSMessage:

        if status is not None:
            try:
                return SMSMessage.objects.get(businessman=user, id=sms_id, status=status)
            except ObjectDoesNotExist as ex:
                if field_name is not None:
                    raise ApplicationErrorCodes.get_field_error(field_name, ApplicationErrorCodes.RECORD_NOT_FOUND, ex)
                else:
                    raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)
        else:
            try:
                return SMSMessage.objects.get(businessman=user, id=sms_id)
            except ObjectDoesNotExist as ex:
                if field_name is not None:
                    raise ApplicationErrorCodes.get_field_error(field_name, ApplicationErrorCodes.RECORD_NOT_FOUND, ex)
                else:
                    raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)


sms_message_service = SMSMessageService()


def create_unsent_plain_sms(*args, ex: SendSMSException, content: str, user: Businessman, receptors: QuerySet):
    remained_recoptors = receptors.order_by('id').filter(id__gte=ex.failed_on.id).all()
    obj = UnsentPlainSMS.objects.create(businessman=user, message=content)
    obj.customers.add(*remained_recoptors)
    obj.save()


def create_unsent_template_sms(*args, ex: SendSMSException, template: str, businessman: Businessman,
                               receptors: QuerySet):
    remained_receptors = receptors.order_by('id').filter(id__gte=ex.failed_on.id).all()
    obj = UnsentTemplateSMS.objects.create(businessman=businessman, template=template)
    obj.customers.add(*remained_receptors)
    obj.save()


def send_plain_sms(*args, businessman: Businessman, customer_ids: List[int], message: str) -> SMSPanelInfo:
    from panelprofile.services import sms_panel_info_service
    from customers.services import customer_service
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    customers = customer_service.get_bsuinessman_customers_by_ids(businessman, customer_ids)
    if customers.count() == 0:
        raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)
    sms = SMSMessage.objects.create(message=message, businessman=businessman, message_type=SMSMessage.TYPE_PLAIN,
                                    status=SMSMessage.STATUS_PENDING)
    SMSMessageReceivers.objects.bulk_create(
        [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers
         ])
    sms.save()
    sms.set_reserved_credit_by_receivers()
    return info


def send_plain_sms_to_all(*args, businessman: Businessman, message: str):
    from customers.services import customer_service
    from panelprofile.services import sms_panel_info_service
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    sms = SMSMessage.objects.create(message=message, businessman=businessman, message_type=SMSMessage.TYPE_PLAIN)
    SMSMessageReceivers.objects.bulk_create(
        [SMSMessageReceivers(sms_message=sms, customer=c) for c in
         customer_service.get_businessman_customers(businessman).all()
         ])
    sms.set_reserved_credit_by_receivers()
    return info


def send_by_template(
        *args,
        businessman: Businessman, customer_ids: List[int],
        template: int) -> SMSPanelInfo:
    from customers.services import customer_service
    from panelprofile.services import sms_panel_info_service
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    template = _get_template_by_id(businessman=businessman, template=template, error_field_name="template")
    customers = customer_service.get_bsuinessman_customers_by_ids(businessman, customer_ids)
    if customers.count() == 0:
        raise ApplicationErrorCodes.get_field_error("customers", ApplicationErrorCodes.RECORD_NOT_FOUND)
    _send_by_template(businessman=businessman, customers=customers, template=template.content,
                      used_for=SMSMessage.USED_FOR_NONE)
    return info


def send_by_template_to_all(*args, businessman: Businessman, template: int) -> SMSPanelInfo:
    from panelprofile.services import sms_panel_info_service
    temp = _get_template_by_id(businessman=businessman, template=template)
    sms = _send_by_template_to_all(
        businessman=businessman,
        template=temp.content,
        used_for=SMSMessage.USED_FOR_NONE
    )
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    return info


def send_plain_to_group(*args, businessman: Businessman, group_id: int, message: str) -> SMSPanelInfo:
    from panelprofile.services import sms_panel_info_service
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    try:
        group = BusinessmanGroups.get_group_by_id(businessman, group_id)
        _send_plain(businessman=businessman, customers=group.get_all_customers(), message=message)
        return info
    except ObjectDoesNotExist as ex:
        raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)


def send_by_template_to_group(*args, businessman: Businessman, group_id: int, template_id: int) -> SMSPanelInfo:
    from panelprofile.services import sms_panel_info_service
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    template = _get_template_by_id(businessman=businessman, template=template_id, error_field_name="template_id")
    try:
        group = BusinessmanGroups.get_group_by_id(businessman, group_id)
    except ObjectDoesNotExist as ex:
        raise ApplicationErrorCodes.get_field_error("group_id", ApplicationErrorCodes.RECORD_NOT_FOUND, ex)

    _send_by_template(businessman=businessman, customers=group.get_all_customers(), template=template.content)
    return info


def resend_failed_message(*args, businessman: Businessman, sms_id: int) -> SMSPanelInfo:
    from panelprofile.services import sms_panel_info_service
    info = sms_panel_info_service.get_buinessman_sms_panel(businessman)
    sms = _get_message(businessman=businessman, sms_id=sms_id, status=SMSMessage.STATUS_FAILED)
    set_message_to_pending(sms_message=sms)
    return info


def set_message_to_pending(*args, sms_message: SMSMessage):
    has_receivers = has_message_any_receivers(sms_message=sms_message)
    if not has_receivers:
        sms_message.set_done()
    else:
        sms_message.reset_to_pending()
    return sms_message


def update_not_pending_message_text(*args, sms_message: SMSMessage, new_message: str):
    if sms_message.status == SMSMessage.STATUS_PENDING:
        raise ValueError('sms message most not be in pending mode for send')
    sms_message.message = new_message
    sms_message.save()


def content_marketing_message_status_cancel(*args, businessman: Businessman, template: str) -> SMSMessage:
    return _send_by_template_to_all(
        businessman=businessman,
        template=template,
        used_for=SMSMessage.USED_FOR_CONTENT_MARKETING,
        status=SMSMessage.STATUS_CANCLE
    )


def set_content_marketing_message_to_pending(*args, sms_message: SMSMessage):
    return set_message_to_pending(sms_message=sms_message)


def festival_message_status_cancel(*args, businessman: Businessman, template: str) -> SMSMessage:
    return _send_by_template_to_all(
        businessman=businessman,
        template=template,
        used_for=SMSMessage.USED_FOR_FESTIVAL,
        status=SMSMessage.STATUS_CANCLE
    )


def friend_invitation_message(*args, businessman: Businessman, template: str, customer):
    return _send_by_template(businessman=businessman, customers=[customer], template=template,
                             used_for=SMSMessage.USED_FOR_FRIEND_INVITATION)


def send_welcome_message(*args, businessman: Businessman, customer) -> SMSMessage:
    from panelprofile.services import sms_panel_info_service
    wm = get_welcome_message(businessman=businessman)
    has_sms_panel = sms_panel_info_service.has_panel_and_is_active(businessman)
    if not has_sms_panel or not wm.send_message:
        return None
    return _send_by_template(businessman=businessman, customers=[customer], template=wm.message,
                             used_for=SMSMessage.USED_FOR_WELCOME_MESSAGE)


def update_welcome_message(*args, businessman: Businessman, message: str, send_message: bool) -> WelcomeMessage:
    w = get_welcome_message(businessman=businessman)
    w.message = message
    w.send_message = send_message
    w.save()
    return w


def create_sms_template(*args, businessman: Businessman, title: str, content: str) -> SMSTemplate:
    return SMSTemplate.objects.create(businessman=businessman, title=title, content=content)


def _send_by_template_to_all(
        *args,
        businessman: Businessman,
        template: str,
        used_for=SMSMessage.USED_FOR_NONE,
        **kwargs) -> SMSMessage:
    from customers.services import customer_service
    sms = SMSMessage.objects.create(message=template, businessman=businessman, used_for=used_for,
                                    message_type=SMSMessage.TYPE_TEMPLATE, **kwargs)
    _set_receivers_for_sms_message(sms=sms, customers=customer_service.get_businessman_customers(businessman))
    _set_reserved_credit_for_sms_message(sms_message=sms)
    return sms


def _send_by_template(
        *args,
        businessman: Businessman,
        customers: List[Customer],
        template: str,
        used_for=SMSMessage.USED_FOR_NONE, **kwargs) -> SMSMessage:
    sms = SMSMessage.objects.create(
        message=template,
        businessman=businessman,
        message_type=SMSMessage.TYPE_TEMPLATE,
        used_for=used_for, **kwargs)
    SMSMessageReceivers.objects.bulk_create(
        [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers]
    )
    _set_reserved_credit_for_sms_message(sms_message=sms)
    return sms


def _send_plain(
        *args,
        businessman: Businessman,
        customers: QuerySet,
        message: str,
        used_for: str = SMSMessage.USED_FOR_NONE, **kwargs) -> SMSMessage:
    sms = SMSMessage.objects.create(
        message=message,
        businessman=businessman,
        message_type=SMSMessage.TYPE_PLAIN,
        used_for=used_for, **kwargs)
    SMSMessageReceivers.objects.bulk_create(
        [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers]
    )
    _set_reserved_credit_for_sms_message(sms_message=sms)
    return sms


def _set_receivers_for_sms_message(*args, sms: SMSMessage, customers: QuerySet):
    SMSMessageReceivers.objects.bulk_create(
        [SMSMessageReceivers(sms_message=sms, customer=c) for c in customers
         ])
    sms.save()


def _set_reserved_credit_for_sms_message(*args, sms_message: SMSMessage):
    count = SMSMessageReceivers.objects.filter(sms_message=sms_message, is_sent=False).count()
    sms_message.reserved_credit = count * max_message_cost
    sms_message.save()
