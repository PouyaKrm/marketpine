import os
import sys
import threading
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CRM.settings'
import django

django.setup()

from scripts.sms_send_script import run_sms
from scripts.invitate_welcome_sms import run_invite_welcome_message


if __name__ == '__main__':
    # threading.Thread(target=run_sms).start()
    # threading.Thread(target=run_invite_welcome_message).start()
    run_invite_welcome_message()
