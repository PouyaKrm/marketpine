import os
import sys
import threading
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
import django

django.setup()

import logging
import threading

from background_task import background
from django.conf import settings
from django.db.models import QuerySet
from django.db.models.query_utils import Q

from common.util.kavenegar_local import APIException, KavenegarMessageStatus
from common.util.sms_panel import messanging
from smspanel.models import SMSMessage, SMSMessageReceivers, SentSMS
from smspanel.selectors import has_message_any_receivers
from smspanel.template_renderers import get_renderer_object_based_on_sms_message_used
from users.models import Businessman, Customer


class BaseSendMessageThread(threading.Thread):
    def __init__(self, api_key: str, sms_message: SMSMessage, receivers: list, message: str):
        super().__init__()
        self.api_key = api_key
        self.sms_message = sms_message
        self._set_receivers_phones(receivers)
        self.receivers = receivers
        self._set_receivers_phones(receivers)
        self.message = message
        self.success_finish = False
        self.failed = False
        self.fail_exception = None
        self.failed_on_low_credit = False
        self.result = None
        self.receiver_ids = [r.id for r in receivers]

    def run(self):
        raise NotImplemented('run method must be implemented')

    def _set_receivers_phones(self, receivers):
        self.phones = [self._get_customer_from_receiver(rec).phone for rec in receivers]

    def _get_customer_from_receiver(self, r) -> Customer:
        raise NotImplemented('method must be implemented')


class SendPlainMessageThread(BaseSendMessageThread):

    def __init__(self, api_key: str, sms_message: SMSMessage, receivers: list, message: str):
        super().__init__(api_key, sms_message, receivers, message)

    def run(self):
        api = messanging.ClientSMSMessage(self.api_key)
        try:

            self.result = api.send_plain(self.phones, self.message)
            self.success_finish = True
        except Exception as e:
            if isinstance(e, APIException) and e.status == KavenegarMessageStatus.NOT_ENOUGH_CREDIT:
                self.failed_on_low_credit = True
            self.failed = True
            self.fail_exception = e
            if isinstance(e, APIException) and e.status == KavenegarMessageStatus.NOT_ENOUGH_CREDIT:
                self.failed_on_low_credit = True

    def _get_customer_from_receiver(self, r) -> Customer:
        return r.customer


class SendTemplateMessageThread(BaseSendMessageThread):

    def __init__(self, api_key, sms_message, receivers: list, message: str):
        super().__init__(api_key, sms_message, receivers, message)
        self.messages = []
        self.phones = []

    def __render_messages(self):
        renderer = get_renderer_object_based_on_sms_message_used(self.sms_message)
        for r in self.receivers:
            message = renderer.render(self._get_customer_from_receiver(r))
            if message is not None:
                self.messages.append(message)
                self.phones.append(self._get_customer_from_receiver(r).phone)

    def run(self):

        try:
            self.__render_messages()
        except ValueError as e:
            self.failed = True
            self.fail_exception = e
            return

        try:
            messenger = messanging.ClientSMSMessage(self.sms_message.businessman.smspanelinfo.api_key)
            self.result = messenger.send_array(self.phones, self.messages)
            self.success_finish = True
        except Exception as e:
            if isinstance(e, APIException) and e.status == KavenegarMessageStatus.NOT_ENOUGH_CREDIT:
                self.failed_on_low_credit = True
            self.failed = True
            self.fail_exception = e

    def _get_customer_from_receiver(self, r) -> Customer:
        return r.customer


class SendMessageTaskQueue:

    def __init__(self):
        self.number_of_threads = settings.SMS_PANEL['SEND_THREADS_NUMBER']
        self.page_size = settings.SMS_PANEL['SEND_TEMPLATE_PAGE_SIZE']
        self.max_fail_attempts = settings.SMS_PANEL['MAX_SEND_FAIL_ATTEMPTS']
        self.threads = []

    def any_pending_message_remained(self):
        return SMSMessage.objects.filter(status=SMSMessage.STATUS_PENDING).exclude(
            Q(used_for=SMSMessage.USED_FOR_FRIEND_INVITATION)
            | Q(used_for=SMSMessage.USED_FOR_WELCOME_MESSAGE)).count() > 0

    def __has_remaining_receivers(self, sms_message):
        return SMSMessageReceivers.objects.filter(sms_message=sms_message, is_sent=False).count() > 0

    def __get_receivers_by_sms_message(self, sms_message) -> QuerySet:
        return SMSMessageReceivers.objects.filter(sms_message=sms_message)

    def __set_threads_by_receivers(self, api_key, sms_message: SMSMessage, receivers: list, message: str):

        self.threads = []

        if sms_message.message_type == SMSMessage.TYPE_PLAIN:
            for f in receivers:
                self.threads.append(SendPlainMessageThread(api_key, sms_message, f, message))

        else:
            for f in receivers:
                self.threads.append(SendTemplateMessageThread(api_key, sms_message, f, message))

    def __set_unsent_receivers_send_threads(self, sms_message: SMSMessage):
        receiver_count = self.__get_receivers_by_sms_message(sms_message).filter(is_sent=False).all().count()
        receivers = []

        if receiver_count <= self.number_of_threads * self.page_size:
            page_size_chunk = int(receiver_count / self.page_size)
            remained = receiver_count % self.page_size

            for i in range(page_size_chunk):
                receivers.append(self.__get_receivers_by_sms_message(sms_message).all()[
                                 i * self.page_size: self.page_size * (i + 1)])

            if remained > 0:
                receivers.append(self.__get_receivers_by_sms_message(sms_message).all()[
                                 page_size_chunk * self.page_size: page_size_chunk * self.page_size + remained])

        else:
            for i in range(self.number_of_threads):
                receivers.append(self.__get_receivers_by_sms_message(sms_message).all()[
                                 i * self.page_size: self.page_size * (i + 1)])

        self.__set_threads_by_receivers(sms_message.businessman.smspanelinfo.api_key, sms_message, receivers,
                                        sms_message.message)

    def _get_oldest_pending_message(self) -> SMSMessage:
        if not self.any_pending_message_remained():
            return None
        return SMSMessage.objects.filter(
            status=SMSMessage.STATUS_PENDING
        ).order_by(
            'create_date'
        ).filter(
            used_for=SMSMessage.USED_FOR_NONE
        ).first()

    def __create_sent_messages(self, sms_message: SMSMessage, result: list, businessman: Businessman):
        sent = []
        total_cost = 0
        for c in result:
            total_cost += c['cost']
            sms = SentSMS(sms_message=sms_message, message_id=c['messageid'],
                          receptor=c['receptor'], message=c['message'],
                          sender=c['sender'], cost=c['cost'],
                          status=c['status'], status_text=c['statustext'],
                          date=c['date']
                          )
            sent.append(sms)
        SentSMS.objects.bulk_create(sent)
        return total_cost

    def _set_message_status_and_empty_threads(self, sms_message):

        fail_count = 0

        for t in self.threads:
            if t.failed:
                fail_count += 1

        if fail_count == len(self.threads):
            sms_message.increase_send_fail_and_set_failed()

        elif not self.__has_remaining_receivers(sms_message):
            sms_message.set_done()

        self.threads = []

    def run_send_threads(self):
        sms_message = self._get_oldest_pending_message()
        if sms_message is None:
            return
        if not has_message_any_receivers(sms_message=sms_message):
            sms_message.set_done()
            return

        self.__set_unsent_receivers_send_threads(sms_message)
        for t in self.threads:
            t.start()

        for t in self.threads:
            t.join()

        costs = 0
        for t in self.threads:

            if t.failed:
                logging.error(t.fail_exception)
            if not t.success_finish:
                continue

            SMSMessageReceivers.objects.filter(id__in=t.receiver_ids).delete()

            costs += self.__create_sent_messages(sms_message, t.result, sms_message.businessman)
        self._set_message_status_and_empty_threads(sms_message)
        try:
            sms_message.businessman.smspanelinfo.refresh_credit()
        except Exception as e:
            sms_message.businessman.smspanelinfo.reduce_credit_local(costs)
            logging.error(e)


def configure() -> SendMessageTaskQueue:
    logging.basicConfig(filename='errors.log', format='%(levelname)s %(asctime)s : %(message)s', level=logging.ERROR)
    return SendMessageTaskQueue()


send_sms_task = configure()


@background()
def run_send_sms_task():
    send_sms_task.run_send_threads()

# task = None
# #
# if __name__ == '__main__':
#     task = configure()
#
# while True:
#     task.run_send_threads()
#     time.sleep(10)

# def run_sms():
#     task = configure()
#     while True:
#         task.run_send_threads()
#         time.sleep(10)
