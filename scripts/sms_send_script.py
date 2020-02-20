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
from common.util.sms_panel.helpers import message_id_and_receptor_from_sms_result


class SendMessageThread(threading.Thread):

    def __init__(self, api_key: str, receivers: list, message: str):
        super().__init__()
        self.api_key = api_key
        self.receivers = receivers
        self.phones = [rec.customer.phone for rec in receivers]
        self.message = message
        self.success_finish = False
        self.failed = False
        self.fail_exception = None
        self.result = None
        self.receiver_ids = [r.id for r in receivers]

    def run(self):
        api = messanging.ClientSMSMessage(self.api_key)
        try:

            self.result = api.send_plain(self.phones, self.message)
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

    def __set_threads_by_receivers(self, api_key, receivers: list, message: str):
        threads = []
        for f in receivers:
            threads.append(SendMessageThread(api_key, f, message))
        self.threads = threads

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

        self.__set_threads_by_receivers(sms_message.businessman.smspanelinfo.api_key, receivers, sms_message.message)

    def __get_oldest_pending_message(self) -> SMSMessage:
        if not self.any_pending_message_remained():
            return None
        return SMSMessage.objects.filter(status=SMSMessage.PENDING).order_by('create_date').first()


    def __create_sent_messages(self, result: list, businessman: Businessman):

        converted = message_id_and_receptor_from_sms_result(result)
        SentSMS.objects.bulk_create([
            SentSMS(businessman=businessman, message_id=c['message_id'], receptor=c['receptor']) for c in converted
        ])

    def __set_message_status_and_empty_threads(self, sms_message):

        fail_count = 0

        for t in self.threads:
            if t.fialed:
                fail_count += 1

        if fail_count == len(self.threads):
            sms_message.increase_send_fail()

            if sms_message.send_fail_attempts >= self.max_fail_attempts:
                sms_message.set_failed()
            return

        if not self.__has_remaining_receivers(sms_message):
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

            for t in self.threads:

                if not t.success_finish:
                    continue

                SMSMessageReceivers.objects.filter(id__in=t.receiver_ids).update(is_sent=True)

                self.__create_sent_messages(t.result, sms_message.businessman)
            self.__set_message_status_and_empty_threads(sms_message)





def get_customers_phone(customers):
    return [c.phone for c in customers]


def any_pending_message_remained():
    return SMSMessage.objects.filter(status=SMSMessage.PENDING).count() > 0


task = SendMessageTaskQueue()

while True:
    task.run_send_threads()
    time.sleep(10)
