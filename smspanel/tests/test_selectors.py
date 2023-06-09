from django_mock_queries.query import MockSet, MockModel

from base_app.error_codes import ApplicationErrorException
from base_app.test_utils import get_model_list_ids, count_model_queryset_by_ids
from smspanel.selectors import get_failed_messages, get_welcome_message, get_sent_sms, get_pending_messages, \
    get_sms_template_by_id, get_reserved_credit_of_pending_messages, has_message_any_receivers, _get_message, \
    get_sms_templates, get_sent_sms_by_messageid

from smspanel.tests.sms_panel_test_fixtures import *

pytestmark = pytest.mark.unit


@pytest.fixture
def mocked_sent_sms(mocker) -> MockSet:
    qs = MockSet(
        MockModel(mock_name='m1', message_id='fake')
    )
    mocker.patch('smspanel.models.SentSMS.objects', qs)
    return qs


def test__get_failed_messages__success(mocker, sms_message_failed_list_1):
    b = sms_message_failed_list_1[0].businessman

    result = get_failed_messages(businessman=b)

    ids = get_model_list_ids(sms_message_failed_list_1)
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
    ids = get_model_list_ids(sent_sms_list_1)
    b = sent_sms_list_1[0].sms_message.businessman

    result = get_sent_sms(businessman=b)

    count = result.filter(id__in=ids).count()
    assert count == len(ids)


def test__get_sent_sms__filter(mocker, sent_sms_list_1):
    r = sent_sms_list_1[0].receptor
    b = sent_sms_list_1[0].sms_message.businessman
    filtered = list(filter(lambda e: e.receptor == r, sent_sms_list_1))
    ids = get_model_list_ids(filtered)

    result = get_sent_sms(businessman=b, receptor_phone=r)

    count = result.filter(id__in=ids).count()
    assert count == len(ids)


def test__get_pending_messages__success(mocker, sms_message_pending_list_1):
    b = sms_message_pending_list_1[0].businessman
    ids = get_model_list_ids(sms_message_pending_list_1)

    result = get_pending_messages(businessman=b)

    count = count_model_queryset_by_ids(result, ids)
    assert count == len(ids)


def test___get_template_by_id__does_not_exist_with_field_error(mocker, businessman_1: Businessman):
    with pytest.raises(ApplicationErrorException) as cx:
        get_sms_template_by_id(businessman=businessman_1, template_id=1, error_field_name='field')


def test___get_template_by_id__does_not_exist_without_field_error(mocker, businessman_1: Businessman):
    with pytest.raises(ApplicationErrorException) as cx:
        get_sms_template_by_id(businessman=businessman_1, template_id=1)


def test___get_template_by_id__success(mocker, sms_template_1):
    result = get_sms_template_by_id(businessman=sms_template_1.businessman, template_id=sms_template_1.id)

    assert result == sms_template_1


def test__get_reserved_credit_of_pending_messages__success(mocker, sms_message_pending_list_1):
    credit_sum = sum(map(lambda e: e.reserved_credit, sms_message_pending_list_1))

    result = get_reserved_credit_of_pending_messages(businessman=sms_message_pending_list_1[0].businessman)

    assert credit_sum == result


def test__has_message_any_receivers(mocker, sms_message_with_receivers):
    result = has_message_any_receivers(sms_message=sms_message_with_receivers[0])

    assert result


_get_message_error_test_data = [
    (None, None),
    ('fake', None),
    (None, SMSMessage.STATUS_PENDING),
    ('fake', SMSMessage.STATUS_PENDING)
]


@pytest.mark.parametrize('error_field, status', _get_message_error_test_data)
def test___get_message__raises_error(mocker, error_field, status, businessman_1: Businessman):
    with pytest.raises(ApplicationErrorException) as cx:
        _get_message(businessman=businessman_1, sms_id=1, status=status, field_name=error_field)


@pytest.mark.parametrize('status', [None, SMSMessage.STATUS_PENDING])
def test___get_message__success(mocker, status, sms_message_pending_1):
    result = _get_message(businessman=sms_message_pending_1.businessman, sms_id=sms_message_pending_1.id,
                          status=status)

    assert result == sms_message_pending_1


def test__get_sms_templates__success(mocker, businessman_1, sms_template_list):
    result = get_sms_templates(businessman=businessman_1)

    assert all(e in result for e in sms_template_list)


def test__get_sent_sms_by_messageid__not_found(mocked_sent_sms):
    first = mocked_sent_sms.first()

    result = get_sent_sms_by_messageid(messageid=first.message_id + '1')

    assert result is None


def test__get_sent_sms_by_messageid__success(mocked_sent_sms):
    first = mocked_sent_sms.first()

    result = get_sent_sms_by_messageid(messageid=first.message_id)

    assert result == first
