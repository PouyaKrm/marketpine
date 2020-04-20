import logging
import time

from background_task import background
from django.db.models.query_utils import Q

from smspanel.background_jobs.sms_send_script import SendMessageTaskQueue
from smspanel.models import SMSMessage
from django.conf import settings

max_fail_attempts = settings.SMS_PANEL['MAX_SEND_FAIL_ATTEMPTS']


class WelcomeInviteSmsMessage(SendMessageTaskQueue):

    def any_pending_message_remained(self):
        return SMSMessage.objects.filter(status=SMSMessage.STATUS_PENDING).filter(
            Q(used_for=SMSMessage.USED_FOR_WELCOME_MESSAGE)
            | Q(used_for=SMSMessage.USED_FOR_FRIEND_INVITATION)).exists()

    def _get_oldest_pending_message(self) -> SMSMessage:
        if not self.any_pending_message_remained():
            return None
        return SMSMessage.objects.order_by('send_fail_attempts', 'create_date').filter(
            status=SMSMessage.STATUS_PENDING).filter(
            Q(used_for=SMSMessage.USED_FOR_WELCOME_MESSAGE)
            | Q(used_for=SMSMessage.USED_FOR_FRIEND_INVITATION)).first()

    def _set_message_status_and_empty_threads(self, sms_message: SMSMessage):

        count = 0
        not_enough_credit_count = 0
        for t in self.threads:
            if t.failed:
                count += 1
                if t.failed_on_low_credit:
                    not_enough_credit_count += 1
        all_threads_failed = count == len(self.threads)
        all_threads_failed_on_low_credit = not_enough_credit_count == len(self.threads)
        self.threads = []
        if all_threads_failed:
            sms_message.just_increase_fail_count()
            if sms_message.send_fail_attempts >= max_fail_attempts:
                sms_message.set_fail()
                return
        if all_threads_failed_on_low_credit:
            sms_message.set_status_wait_charge()
        if count == 0 and not_enough_credit_count == 0:
            sms_message.set_done()


def configure() -> SendMessageTaskQueue:
    logging.basicConfig(filename='wi_errors.log', format='%(levelname)s %(asctime)s : %(message)s', level=logging.ERROR)
    return WelcomeInviteSmsMessage()


back_task = configure()


@background()
def run_send_invite_sms_task():
    back_task.run_send_threads()

# def run_invite_welcome_message():
#     task = configure()
#     while True:
#         task.run_send_threads()
#         time.sleep(1)
