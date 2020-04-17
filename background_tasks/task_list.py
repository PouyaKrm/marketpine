import os
import sys
import threading
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
import django

django.setup()

from .sms_send_task import SendMessageTaskQueue


back_tasks = [
    (1000, 'send sms', SendMessageTaskQueue)
]
