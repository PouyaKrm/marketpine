from pyrogram import Client

from CRM.settings import TELEGRAM_api_id, TELEGRAM_api_hash

app = Client("my_account", api_hash=TELEGRAM_api_hash,api_id=TELEGRAM_api_id)

app.send_messag