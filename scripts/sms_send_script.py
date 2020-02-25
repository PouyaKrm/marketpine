import os
import time
import threading

from django.db.models import QuerySet
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CRM.settings")
import django

django.setup()

from django.conf import settings
from smspanel.models import SMSMessage, SMSMessageReceivers, SentSMS
from users.models import Businessman
from common.util.sms_panel import messanging
from common.util.sms_panel.helpers import message_id_receptor_cost_sms
from scripts.template_renderers import get_renderer_object_based_on_sms_message_used


class BaseSendMessageThread(threading.Thread):
    def __init__(self, api_key: str, sms_message: SMSMessage, receivers: list, message: str):
        super().__init__()
        self.api_key = api_key
        self.sms_message = sms_message
        self.receivers = receivers
        self.phones = [rec.customer.phone for rec in receivers]
        self.message = message
        self.success_finish = False
        self.failed = False
        self.fail_exception = None
        self.result = None
        self.receiver_ids = [r.id for r in receivers]

    def run(self):
        raise NotImplemented('run method must be implemented')


class SendPlainMessageThread(BaseSendMessageThread):

    def __init__(self, api_key: str, sms_message: SMSMessage, receivers: list, message: str):
        super().__init__(api_key, sms_message, receivers, message)
        # self.api_key = api_key
        # self.receivers = receivers
        # self.phones = [rec.customer.phone for rec in receivers]
        # self.message = message
        # self.success_finish = False
        # self.failed = False
        # self.fail_exception = None
        # self.result = None
        # self.receiver_ids = [r.id for r in receivers]

    def run(self):
        api = messanging.ClientSMSMessage(self.api_key)
        try:

            self.result = api.send_plain(self.phones, self.message)
            self.success_finish = True
        except Exception as e:
            self.failed = True
            self.fail_exception = e


class SendTemplateMessageThread(BaseSendMessageThread):

    def __init__(self, api_key, sms_message, receivers: list, message: str):
        super().__init__(api_key, sms_message, receivers, message)
        self.messages = []
        self.phones = []

    def __render_messages(self):
        renderer = get_renderer_object_based_on_sms_message_used('45')
        for r in self.receivers:
            message = renderer.render(self.sms_message, r)
            if message is not None:
                self.messages.append(message)
                self.phones.append(r.customer.phone)

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
            self.failed = True
            self.fail_exception = e


class SendMessageTaskQueue:

    def __init__(self):
        self.number_of_threads = settings.SMS_PANEL['SEND_THREADS_NUMBER']
        self.page_size = settings.SMS_PANEL['SEND_TEMPLATE_PAGE_SIZE']
        self.max_fail_attempts = settings.SMS_PANEL['MAX_SEND_FAIL_ATTEMPTS']
        self.threads = []

    def any_pending_message_remained(self):
        return SMSMessage.objects.filter(status=SMSMessage.PENDING).count() > 0

    def __has_remaining_receivers(self, sms_message):
        return SMSMessageReceivers.objects.filter(sms_message=sms_message, is_sent=False).count() > 0

    def __get_receivers_by_sms_message(self, sms_message) -> QuerySet:
        return SMSMessageReceivers.objects.filter(sms_message=sms_message)

    def __set_threads_by_receivers(self, api_key, sms_message: SMSMessage, receivers: list, message: str):

        self.threads = []

        if sms_message.message_type == SMSMessage.PLAIN:
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
                receivers.append(self.__get_receivers_by_sms_message(sms_message).all()[i * self.page_size: self.page_size * (i + 1)])


            if remained > 0:
                receivers.append(self.__get_receivers_by_sms_message(sms_message).all()[page_size_chunk * self.page_size: page_size_chunk * self.page_size  + remained])

        else:
            for i in range(self.number_of_threads):
                receivers.append(self.__get_receivers_by_sms_message(sms_message).all()[i * self.page_size: self.page_size * (i + 1)])

        self.__set_threads_by_receivers(sms_message.businessman.smspanelinfo.api_key, sms_message, receivers, sms_message.message)

    def __get_oldest_pending_message(self) -> SMSMessage:
        if not self.any_pending_message_remained():
            return None
        return SMSMessage.objects.filter(status=SMSMessage.PENDING).order_by('create_date').first()

    def __create_sent_messages(self, result: list, businessman: Businessman):

        converted = message_id_receptor_cost_sms(result)
        SentSMS.objects.bulk_create([
            SentSMS(businessman=businessman, message_id=c['message_id'], receptor=c['receptor']) for c in converted
        ])

        total_cost = 0
        for r in converted:
            total_cost += r['cost']
        return total_cost

    def __set_message_status_and_empty_threads(self, sms_message):

        fail_count = 0

        for t in self.threads:
            if t.failed:
                fail_count += 1

        if fail_count == len(self.threads):
            sms_message.increase_send_fail()

            if sms_message.send_fail_attempts >= self.max_fail_attempts:
                sms_message.set_failed()

        elif not self.__has_remaining_receivers(sms_message):
            sms_message.set_done()

        self.threads = []

    def run_send_threads(self):
        sms_message = self.__get_oldest_pending_message()
        if sms_message is not None:
            self.__set_unsent_receivers_send_threads(sms_message)
            for t in self.threads:
                t.start()

            for t in self.threads:
                t.join()

            costs = 0
            for t in self.threads:

                if not t.success_finish:
                    continue

                SMSMessageReceivers.objects.filter(id__in=t.receiver_ids).update(is_sent=True)

                costs += self.__create_sent_messages(t.result, sms_message.businessman)
            self.__set_message_status_and_empty_threads(sms_message)
            try:
                sms_message.businessman.smspanelinfo.refresh_credit()
            except Exception as e:
                sms_message.businessman.smspanelinfo.reduce_credit(costs)





def get_customers_phone(customers):
    return [c.phone for c in customers]


def any_pending_message_remained():
    return SMSMessage.objects.filter(status=SMSMessage.PENDING).count() > 0


task = SendMessageTaskQueue()

while True:
    task.run_send_threads()
    time.sleep(10)
