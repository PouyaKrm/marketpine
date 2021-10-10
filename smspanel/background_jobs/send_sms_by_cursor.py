import os
import sys
from os.path import dirname, abspath

from background_task import background
from django.db.models.query_utils import Q

from smspanel.background_jobs.sms_send_script import SendPlainMessageThread, SendTemplateMessageThread
from smspanel.services import increase_send_failed_attempts, create_sent_sms_from_send_array_result
#
# sys.path.append(dirname(dirname(abspath(__file__))))
# os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
import django

# django.setup()

from typing import List, Optional

from django.db.models import QuerySet

from smspanel.models import SMSMessage
from users.models import Customer
from django.conf import settings
import logging

logger = logging.getLogger('django')

threads_num = settings.SMS_PANEL['SEND_THREADS_NUMBER']
page_size = settings.SMS_PANEL['SEND_TEMPLATE_PAGE_SIZE']


class SendPlainByCursorThread(SendPlainMessageThread):

    def _get_customer_from_receiver(self, r) -> Customer:
        return r


class SendTemplateByCursorThread(SendTemplateMessageThread):

    def _get_customer_from_receiver(self, r) -> Customer:
        return r


def slice_receivers(sms_message: SMSMessage) -> List[List[Customer]]:
    receiver_customers = Customer.objects.filter(
        businessmans=sms_message.businessman
    )
    if sms_message.used_for == SMSMessage.USED_FOR_SEND_TO_GROUP:
        receiver_customers = receiver_customers.filter(connected_groups=sms_message.related_receiver_group.group)
    receiver_customers = receiver_customers.order_by(
        'id'
    ).filter(
        id__gte=sms_message.current_receiver_id,
        id__lte=sms_message.last_receiver_id
    )

    receiver_count = receiver_customers.count()
    receivers = []

    if receiver_count <= (threads_num * page_size):
        page_size_chunk = int(receiver_count / page_size)
        remained = receiver_count % page_size

        for i in range(page_size_chunk):
            receivers.append(list(receiver_customers.all()[i * page_size: page_size * (i + 1)]))

        if remained > 0:
            receivers.append(
                list(receiver_customers.all()[page_size_chunk * page_size: page_size_chunk * page_size + remained]))

    else:
        for i in range(threads_num):
            receivers.append(list(receiver_customers.all()[i * page_size: page_size * (i + 1)]))

    return receivers


def get_pending_message() -> Optional[SMSMessage]:
    return SMSMessage.objects.order_by(
        'create_date'
    ).filter(
        status=SMSMessage.STATUS_PENDING
    ).filter(
        Q(used_for=SMSMessage.USED_FOR_SEND_TO_ALL)
        | Q(used_for=SMSMessage.USED_FOR_CONTENT_MARKETING)
        | Q(used_for=SMSMessage.USED_FOR_FESTIVAL)
        | Q(used_for=SMSMessage.USED_FOR_SEND_TO_GROUP)
    ).first()


@background()
def send_sms_by_cursor():
    sms = get_pending_message()
    if sms is None:
        return
    receivers = slice_receivers(sms)
    if len(receivers) == 0:
        sms.set_done()
        return
    threads = []
    if sms.is_message_type_plain():
        for i in receivers:
            t = SendPlainByCursorThread(
                sms.businessman.smspanelinfo.api_key,
                sms,
                i, sms.message
            )
            threads.append(t)

    else:
        for i in receivers:
            t = SendTemplateByCursorThread(sms.businessman.smspanelinfo.api_key, sms, i, sms.message)
            threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    failed_threads = list(filter(lambda thread: thread.failed, threads))
    success_threads = list(filter(lambda thread: not thread.failed, threads))
    costs = 0
    for t in success_threads:
        if t.result is not None:
            costs += create_sent_sms_from_send_array_result(sms_message=sms, result=t.result)

    for t in failed_threads:
        if t.fail_exception is not None:
            logger.error(t.fail_exception)
        if t.failed_on_low_credit:
            sms.set_status_wait_charge()

    try:
        sms.businessman.smspanelinfo.refresh_credit()
    except Exception as e:
        sms.businessman.smspanelinfo.reduce_credit_local(costs)
        logger.error(e)

    if len(failed_threads) > (len(threads) / 2):
        increase_send_failed_attempts(sms_message=sms)
    else:
        last_id = receivers[-1][-1].id
        if last_id >= sms.last_receiver_id:
            sms.current_receiver_id = last_id
            sms.set_done()
        else:
            sms.current_receiver_id = last_id + 1
        sms.save()

#
# if __name__ == '__main__':
#     send_sms_by_cursor()
