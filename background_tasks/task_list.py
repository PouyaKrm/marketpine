import os
import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
import django

django.setup()

from background_tasks.tasks.sms_send_task import SendMessageTaskQueue
from background_tasks.tasks.invitate_welcome_sms import WelcomeInviteSmsMessage


back_tasks = [
    (1000, 'send sms', SendMessageTaskQueue),
    (1001, 'welcome invite sms', WelcomeInviteSmsMessage)
]
