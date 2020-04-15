import logging
import time

from django.db.models.query_utils import Q

from scripts.sms_send_script import SendMessageTaskQueue
from smspanel.models import SMSMessage


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
        if count == len(self.threads):
            sms_message.just_increase_fail_count()
        if not_enough_credit_count == len(self.threads):
            sms_message.set_status_wait_charge()

        self.threads = []


def configure() -> SendMessageTaskQueue:
    logging.basicConfig(filename='wi_errors.log', format='%(levelname)s %(asctime)s : %(message)s', level=logging.ERROR)
    return WelcomeInviteSmsMessage()


def run_invite_welcome_message():
    task = configure()
    while True:
        task.run_send_threads()
        time.sleep(1)
