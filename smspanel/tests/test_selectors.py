from base_app.test_utils import get_model_ids
from smspanel.selectors import get_failed_messages, get_welcome_message, get_sent_sms

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


def test__get_sent_sms__get_all(mocker, sent_sms_list_1):
    ids = get_model_ids(sent_sms_list_1)
    b = sent_sms_list_1[0].sms_message.businessman

    result = get_sent_sms(businessman=b)

    count = result.filter(id__in=ids).count()
    assert count == len(ids)


def test__get_sent_sms__filter(mocker, sent_sms_list_1):
    r = sent_sms_list_1[0].receptor
    b = sent_sms_list_1[0].sms_message.businessman
    filtered = list(filter(lambda e: e.receptor == r, sent_sms_list_1))
    ids = get_model_ids(filtered)

    result = get_sent_sms(businessman=b, receptor_phone=r)

    count = result.filter(id__in=ids).count()
    assert count == len(ids)
