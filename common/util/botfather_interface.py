# TODO: support multiple accounts or a account pool of somekind to surpass telegram 20 bot limit per account limitation

import re

import pyrogram
from pyrogram import Client
from tgintegration import BotIntegrationClient
from bot import setup_django

from CRM.settings import TELEGRAM_api_id, TELEGRAM_api_hash


def mk_client():
    client = BotIntegrationClient(bot_under_test='@BotFather',
                                  session_name="armor007",
                                  api_hash=TELEGRAM_api_hash,
                                  api_id=TELEGRAM_api_id,
                                  max_wait_response=8,
                                  min_wait_consecutive=2,
                                  )

    client.start()
    client.send_command_await("cancel", num_expected=1)
    client.stop()
    return client


def newbot(name: str, username: str) -> str:
    client = mk_client()
    client.send_command_await("newbot", num_expected=1)
    client.send_message_await(name, num_expected=1)
    res = client.send_message_await(username, num_expected=1).full_text

    try:
        token = re.search('HTTP API:\n(.+?)\nKeep your', res).group(1)
    except ValueError:
        if res.startswith("Sorry"):
            token = ''
        else:
            raise Exception("This should not happen!")
    finally:
        client.stop()
    return token


def deletebot(username: str) -> bool:
    client = mk_client()
    client.send_command_await("deletebot", num_expected=1)
    if not username.startswith("@"):
        username = "@" + username
    selected = client.send_message_await(username, num_expected=1).full_text
    if selected.startswith("Invalid bot"):
        client.stop()
        return False
    client.send_message_await("Yes, I am totally sure.", num_expected=1)
    client.stop()
    return True


def username_is_available(username: str) -> bool:
    client = Client(session_name="armor007",
                    api_hash=TELEGRAM_api_hash,
                    api_id=TELEGRAM_api_id,
                    )

    client.start()
    try:
        client.get_users(username)
    except pyrogram.api.errors.exceptions.bad_request_400.UsernameNotOccupied:
        return False
    finally:
        client.stop()
    return True
