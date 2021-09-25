from base_app.test_utils import get_model_ids
from smspanel.selectors import get_failed_messages, get_welcome_message

from smspanel.tests.sms_panel_test_fixtures import *


def test__get_failed_messages__success(mocker, sms_message_failed_list_1):
    b = sms_message_failed_list_1[0].businessman

    result = get_failed_messages(user=b)

    ids = get_model_ids(sms_message_failed_list_1)
    count = result.filter(id__in=ids).count()
    assert count == len(sms_message_failed_list_1)


def test__get_welcome_message__create_new(mocker, businessman_1: Businessman):
    w = get_welcome_message(businessman=businessman_1)
    exist = WelcomeMessage.objects.filter(id=w.id).exists()
    assert exist


def test__test__get_welcome_message__already_exist(mocker, welcome_message_1: WelcomeMessage):
    b = welcome_message_1.businessman

    result = get_welcome_message(businessman=b)

    assert result == welcome_message_1
