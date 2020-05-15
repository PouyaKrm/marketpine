from django.core.management.base import BaseCommand

from smspanel.background_jobs.invitate_welcome_sms import run_send_invite_sms_task
from smspanel.background_jobs.sms_send_script import run_send_sms_task


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        run_send_invite_sms_task(repeat=10)
        run_send_sms_task(repeat=10)
