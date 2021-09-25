from base_app.test_utils import get_model_ids
from smspanel.selectors import get_failed_messages


def test_get_failed_messages_success(mocker, sms_message_failed_list_1):
    b = sms_message_failed_list_1[0].businessman

    result = get_failed_messages(user=b)

    ids = get_model_ids(sms_message_failed_list_1)
    count = result.filter(id__in=ids).count()
    assert count == len(sms_message_failed_list_1)
