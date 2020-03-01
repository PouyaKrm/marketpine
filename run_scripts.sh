#! /bin/bash

source ./venv/bin/activate

nohup python ./scripts/sms_send_script.py &
