from django.conf import settings

from base_app.error_codes import ApplicationErrorException
from base_app.tests import *
from panelprofile.models import SMSPanelInfo
# from smspanel.models import SMSMessage, SMSMessageReceivers
# from smspanel.services import send_plain_sms
from smspanel import services
from smspanel.models import SMSMessage, SMSMessageReceivers, SMSTemplate, WelcomeMessage
from smspanel.services import send_by_template, send_by_template_to_all, send_plain_to_group, send_by_template_to_group, \
    resend_failed_message, set_message_to_pending, update_not_pending_message_text, \
    set_content_marketing_message_to_pending, festival_message_status_cancel, friend_invitation_message, \
    send_welcome_message, update_welcome_message, _send_by_template_to_all, _send_by_template, _send_plain, \
    _set_receivers_for_sms_message, _set_reserved_credit_for_sms_message

max_message_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']


@pytest.fixture
def create_sms_message(db, businessman_with_customer_tuple):
    def create_sms(status: str, failed_attempts: int = 0) -> SMSMessage:
        return SMSMessage.objects.create(businessman=businessman_with_customer_tuple[0], status=status,
                                         send_fail_attempts=failed_attempts)

    return create_sms


@pytest.fixture
def sms_message_pending_1(db, create_sms_message) -> SMSMessage:
    return create_sms_message(status=SMSMessage.STATUS_PENDING)


@pytest.fixture
def sms_message_failed_1(db, create_sms_message) -> SMSMessage:
    return create_sms_message(status=SMSMessage.STATUS_FAILED, failed_attempts=10)


@pytest.fixture
def sms_message_with_receivers(db, sms_message_pending_1, businessman_with_customer_tuple) -> Tuple[
    SMSMessage, List[SMSMessageReceivers]]:
    result = []
    for i in businessman_with_customer_tuple[1]:
        s = SMSMessageReceivers.objects.create(sms_message=sms_message_pending_1, customer=i, is_sent=False)
        result.append(s)

    return sms_message_pending_1, result

def mock_sms_panel_info(mocker):
    return_val = SMSPanelInfo()
    mock = mocker.patch('panelprofile.services.sms_panel_info_service.get_buinessman_sms_panel',
                        return_value=return_val)
    return mock


def mock_get_template_by_id(mocker):
    return_val = SMSTemplate(content='fake template')
    mock = mocker.patch('smspanel.services._get_template_by_id', return_value=return_val)
    return mock


def mock_send_by_template_to_all(mocker):
    return_val = SMSMessage()
    mock = mocker.patch('smspanel.services._send_by_template_to_all', return_value=return_val)
    return mock


def mock_get_group_by_id(mocker, raise_exception: bool):
    mock = mocker.patch('smspanel.services.BusinessmanGroups.get_group_by_id')
    ex = None
    if raise_exception:
        ex = ApplicationErrorException({})
        mock.side_effect = ex

    return mock


def mock_send_plain(mocker):
    return_val = SMSMessage()
    mock = mocker.patch('smspanel.services._send_plain', return_value=return_val)
    return mock


def mock_send_by_template(mocker):
    return_val = SMSMessage()
    mock = mocker.patch('smspanel.services._send_by_template', return_value=return_val)
    return mock


def mock_set_sms_message_to_pending(mocker):
    def side_effect_func(sms_message):
        return sms_message

    mock = mocker.patch('smspanel.services.set_message_to_pending')
    mock.side_effect = side_effect_func
    return mock


def mock_get_message(mocker):
    return mocker.patch('smspanel.services._get_message', return_value=SMSMessage())


def mock_get_welcome_message(mocker, send_message=True):
    return mocker.patch(
        'smspanel.services.get_welcome_message',
        return_value=WelcomeMessage(send_message=send_message, message='fake')
    )


def mock_has_sms_panel_and_is_active(mocker, is_active: bool):
    return mocker.patch('panelprofile.services.sms_panel_info_service.has_panel_and_is_active', return_value=is_active)


def mock__set_receivers_for_sms_message(mocker):
    return mocker.patch('smspanel.services._set_receivers_for_sms_message', return_value=[SMSMessageReceivers()])


def mock_get_businessman_customers(mocker):
    return mocker.patch('customers.services.customer_service.get_businessman_customers', return_value=[Customer()])


def mock__set_reserved_credit_for_sms_message(mocker):
    return mocker.patch('smspanel.services._set_reserved_credit_for_sms_message', return_value=None)


def test_send_plain_sms_customer_count_0(mocker, businessman_1: Businessman):
    mock = mock_sms_panel_info(mocker)

    customer_ids = [i for i in range(1, 10)]

    with pytest.raises(ApplicationErrorException):
        services.send_plain_sms(user=businessman_1, customer_ids=customer_ids, message='fake')
    mock.assert_called_once()


def test_send_plain_sms_success(mocker, businessman_with_customer_tuple):
    mock_result = mock_sms_panel_info(mocker)
    customer_ids = list(map(lambda e: e.id, businessman_with_customer_tuple[1]))
    businessman = businessman_with_customer_tuple[0]
    message = 'message'
    result = services.send_plain_sms(user=businessman, customer_ids=customer_ids, message=message)
    mock_result.assert_called_once()
    smsq = SMSMessage.objects.filter(
        businessman=businessman,
        message_type=SMSMessage.TYPE_PLAIN,
        status=SMSMessage.STATUS_PENDING,
        message=message)
    assert smsq.exists()
    sms = smsq.first()

    receivers_count = SMSMessageReceivers.objects.filter(sms_message=sms, customer__id__in=customer_ids).count()
    assert receivers_count == len(customer_ids)
    assert result == mock_result.return_value


def test_send_plain_sms_to_all_success(mocker, businessman_with_customer_tuple):
    mock_result = mock_sms_panel_info(mocker)
    businessman = businessman_with_customer_tuple[0]
    customer_ids = list(map(lambda e: e.id, businessman_with_customer_tuple[1]))
    message = 'message'
    result = services.send_plain_sms_to_all(user=businessman, message=message)
    mock_result.assert_called_once()
    assert result == mock_result.return_value
    smsq = SMSMessage.objects.filter(businessman=businessman, message_type=SMSMessage.TYPE_PLAIN, message=message)
    assert smsq.exists()
    count = SMSMessageReceivers.objects.filter(sms_message=smsq.first(), customer__id__in=customer_ids).count()
    assert count == len(customer_ids)


def test_send_by_template_raises_error(mocker, businessman_1: Businessman):
    mock_result = mock_sms_panel_info(mocker)
    template_mock = mock_get_template_by_id(mocker)
    customer_ids = [i for i in range(1, 10)]
    with pytest.raises(ApplicationErrorException) as cx:
        result = send_by_template(user=businessman_1, customer_ids=customer_ids, template=1)
    mock_result.assert_called_once()
    template_mock.assert_called_once()


def test_send_by_template_success(mocker, businessman_with_customer_tuple):
    mock_result = mock_sms_panel_info(mocker)
    template_mock_result = mock_get_template_by_id(mocker)
    template = template_mock_result.return_value
    businessman = businessman_with_customer_tuple[0]
    customer_ids = list(map(lambda e: e.id, businessman_with_customer_tuple[1]))
    result = send_by_template(user=businessman, customer_ids=customer_ids, template=1)
    mock_result.assert_called_once()
    template_mock_result.assert_called_once()
    assert result == mock_result.return_value
    smsq = SMSMessage.objects.filter(businessman=businessman, message_type=SMSMessage.TYPE_TEMPLATE,
                                     message=template.content)
    assert smsq.exists()
    sms = smsq.first()
    assert sms.message == template.content
    count = SMSMessageReceivers.objects.filter(sms_message=sms, customer__id__in=customer_ids).count()
    assert count == len(customer_ids)


def test_send_by_template_to_all_success(mocker, businessman_1: Businessman):
    info_mock_result = mock_sms_panel_info(mocker)
    get_by_id_mock_result = mock_get_template_by_id(mocker)
    template_to_all_mock_result = mock_send_by_template_to_all(mocker)
    template = get_by_id_mock_result.return_value
    result = send_by_template_to_all(user=businessman_1, template=1)
    info_mock_result.assert_called_once()
    template_to_all_mock_result.assert_called_once_with(user=businessman_1, template=template.content,
                                                        used_for=SMSMessage.USED_FOR_NONE)
    assert result == info_mock_result.return_value


def test_send_plain_to_group_raises_error(mocker, businessman_1: Businessman):
    info_mock = mock_sms_panel_info(mocker)
    group_by_id_mock_result = mock_get_group_by_id(mocker, True)
    plain_mock_result = mock_send_plain(mocker)
    group_id = 1
    with pytest.raises(ApplicationErrorException) as cx:
        send_plain_to_group(user=businessman_1, group_id=group_id, message='fake')
    info_mock.assert_called_once()
    group_by_id_mock_result.assert_called_once_with(businessman_1, group_id)
    plain_mock_result.assert_not_called()


def test_send_plain_to_group_success(mocker, businessman_1: Businessman):
    info_mock = mock_sms_panel_info(mocker)
    group_mock = mock_get_group_by_id(mocker, False)
    plain_mock = mock_send_plain(mocker)
    group_id = 1
    message = 'fake'
    result = send_plain_to_group(user=businessman_1, group_id=group_id, message=message)
    info_mock.assert_called_once()
    group_mock.assert_called_once_with(businessman_1, group_id)
    plain_mock.assert_called_once()
    assert result == info_mock.return_value


def test_send_by_template_to_group_raises_error(mocker, businessman_1: Businessman):
    info_mock = mock_sms_panel_info(mocker)
    template_mock = mock_get_template_by_id(mocker)
    group_mock = mock_get_group_by_id(mocker, True)
    send_by_template_mock = mock_send_by_template(mocker)

    with pytest.raises(ApplicationErrorException) as cx:
        send_by_template_to_group(user=businessman_1, group_id=1, template_id=1)

    info_mock.assert_called_once()
    template_mock.assert_called_once()
    group_mock.assert_called_once()
    send_by_template_mock.assert_not_called()


def test_send_by_template_to_group_success(mocker, businessman_1: Businessman):
    call_params = {'user': Businessman, 'group_id': 1, 'template_id': 1}
    info_mock = mock_sms_panel_info(mocker)
    template_mock = mock_get_template_by_id(mocker)
    group_mock = mock_get_group_by_id(mocker, False)
    send_by_template_mock = mock_send_by_template(mocker)

    result = send_by_template_to_group(**call_params)

    assert result == info_mock.return_value
    info_mock.assert_called_once()
    template_mock.assert_called_once()
    group_mock.assert_called_once()
    send_by_template_mock.assert_called_once()


def test_resend_failed_message_success(mocker, businessman_1: Businessman):
    info_mock = mock_sms_panel_info(mocker)
    message_mock = mock_get_message(mocker)
    set_pending_mock = mock_set_sms_message_to_pending(mocker)
    sms_id = 1

    result = resend_failed_message(businessman_1, sms_id)

    info_mock.assert_called_once()
    message_mock.assert_called_once_with(user=businessman_1, sms_id=sms_id, status=SMSMessage.STATUS_FAILED)
    set_pending_mock.assert_called_once_with(sms_message=message_mock.return_value)
    assert result == info_mock.return_value


def test_set_message_to_pending_set_done(mocker, sms_message_pending_1: SMSMessage):
    mock = mocker.patch('smspanel.services.has_message_any_receivers', return_value=False)

    result = set_message_to_pending(sms_message=sms_message_pending_1)

    mock.assert_called_once()
    assert sms_message_pending_1.status == SMSMessage.STATUS_DONE


def test_set_message_to_pending_set_pending(mocker, sms_message_failed_1: SMSMessage):
    mock = mocker.patch('smspanel.services.has_message_any_receivers', return_value=True)

    result = set_message_to_pending(sms_message=sms_message_failed_1)

    mock.assert_called_once()
    assert sms_message_failed_1.status == SMSMessage.STATUS_PENDING
    assert sms_message_failed_1.send_fail_attempts == 0


def test_update_not_pending_message_text_raises_error(mocker, sms_message_pending_1: SMSMessage):
    with pytest.raises(ValueError) as cx:
        update_not_pending_message_text(sms_message=sms_message_pending_1, new_message='fake')


def test_update_not_pending_message_text_success(mocker, sms_message_failed_1: SMSMessage):
    message = 'fake'

    result = update_not_pending_message_text(sms_message=sms_message_failed_1, new_message=message)

    exist = SMSMessage.objects.filter(id=sms_message_failed_1.id, message=message).exists()
    assert exist


def test_set_content_marketing_message_to_pending_success(mocker, sms_message_failed_1: SMSMessage):
    mock = mock_set_sms_message_to_pending(mocker)

    result = set_content_marketing_message_to_pending(sms_message=sms_message_failed_1)

    mock.assert_called_once_with(sms_message=sms_message_failed_1)


def test_festival_message_status_cancel_success(mocker, businessman_1: Businessman):
    mock = mock_send_by_template_to_all(mocker)
    template = 'template'

    result = festival_message_status_cancel(template=template, user=businessman_1)

    mock.assert_called_once_with(
        user=businessman_1,
        template=template,
        used_for=SMSMessage.USED_FOR_FESTIVAL,
        status=SMSMessage.STATUS_CANCLE
    )


def test_friend_invitation_message_success(mocker, businessman_with_customer_tuple):
    mock = mock_send_by_template(mocker)
    call_params = {
        'user': businessman_with_customer_tuple[0],
        'customer': businessman_with_customer_tuple[1][0],
        'template': 'fake'
    }
    mock_call_params = {**call_params, 'used_for': SMSMessage.USED_FOR_FRIEND_INVITATION}
    mock_call_params['customers'] = [mock_call_params.pop('customer')]

    result = friend_invitation_message(**call_params)

    mock.assert_called_once_with(**mock_call_params)


def test_send_welcome_message_not_has_sms_panel(mocker, businessman_with_customer_tuple):
    welcome_message_mock = mock_get_welcome_message(mocker, True)
    has_panel_mock = mock_has_sms_panel_and_is_active(mocker, False)
    businessman = businessman_with_customer_tuple[0]
    customer = businessman_with_customer_tuple[1][0]

    result = send_welcome_message(user=businessman, customer=customer)

    welcome_message_mock.assert_called_once_with(businessman=businessman)
    has_panel_mock.assert_called_once_with(businessman)
    assert result is None


def test_send_welcome_message_send_message_is_disable(mocker, businessman_with_single_customer_tuple):
    welcome_message_mock = mock_get_welcome_message(mocker, False)
    has_panel_mock = mock_has_sms_panel_and_is_active(mocker, True)
    b = businessman_with_single_customer_tuple[0]
    c = businessman_with_single_customer_tuple[1]

    result = send_welcome_message(user=b, customer=c)

    welcome_message_mock.assert_called_once_with(businessman=b)
    has_panel_mock.assert_called_once_with(b)
    assert result is None


def test_send_welcome_message_success(mocker, businessman_with_single_customer_tuple):
    welcome_message_mock = mock_get_welcome_message(mocker, True)
    has_panel_mock = mock_has_sms_panel_and_is_active(mocker, True)
    send_by_template_mock = mock_send_by_template(mocker)
    b = businessman_with_single_customer_tuple[0]
    c = businessman_with_single_customer_tuple[1]

    result = send_welcome_message(user=b, customer=c)

    welcome_message_mock.assert_called_once_with(businessman=b)
    has_panel_mock.assert_called_once_with(b)
    send_by_template_mock.assert_called_once_with(
        user=b,
        customers=[c],
        template=welcome_message_mock.return_value.message,
        used_for=SMSMessage.USED_FOR_WELCOME_MESSAGE
    )

    assert result is not None


def test_update_welcome_message_success(mocker, businessman_1: Businessman):
    mock = mock_get_welcome_message(mocker, False)
    message = 'new message'
    send_message = True
    mocked_save_method = mocker.patch.object(WelcomeMessage, 'save', return_value=None)

    result = update_welcome_message(businessman=businessman_1, message=message, send_message=send_message)

    mock.assert_called_once_with(businessman=businessman_1)
    mocked_save_method.assert_called_once()
    assert result.message == message
    assert result.send_message == send_message


def test__send_by_template_to_all_success(mocker, businessman_with_customer_tuple):
    mock = mock__set_receivers_for_sms_message(mocker)
    mock_reserved_credit = mock__set_reserved_credit_for_sms_message(mocker)
    customers_mock = mock_get_businessman_customers(mocker)
    b = businessman_with_customer_tuple[0]
    used_for = SMSMessage.USED_FOR_CONTENT_MARKETING
    template = 'fake'

    result = _send_by_template_to_all(user=b, template=template, used_for=used_for)

    smsq = SMSMessage.objects.filter(businessman=b, used_for=used_for, message=template,
                                     message_type=SMSMessage.TYPE_TEMPLATE)
    assert smsq.count() == 1
    assert result == smsq.first()
    mock.assert_called_once_with(sms=result, customers=customers_mock.return_value)
    mock_reserved_credit.assert_called_once_with(sms_message=result)


def test__send_by_template_success(mocker, businessman_with_customer_tuple):
    mock = mock__set_reserved_credit_for_sms_message(mocker)
    b = businessman_with_customer_tuple[0]
    customers = businessman_with_customer_tuple[1]
    c_ids = list(map(lambda e: e.id, customers))
    template = 'fake'
    used_for = SMSMessage.USED_FOR_CONTENT_MARKETING

    result = _send_by_template(user=b, customers=customers, template=template,
                               used_for=used_for)

    smsq = SMSMessage.objects.filter(businessman=b,
                                     message=template,
                                     used_for=used_for,
                                     message_type=SMSMessage.TYPE_TEMPLATE
                                     )
    receivers = SMSMessageReceivers.objects.filter(customer__id__in=c_ids, sms_message=smsq.first())

    assert smsq.count() == 1
    assert result == smsq.first()
    assert receivers.count() == len(c_ids)
    mock.assert_called_once_with(sms_message=result)


def test__send_plain_success(mocker, businessman_with_customer_tuple):
    mock = mock__set_reserved_credit_for_sms_message(mocker)
    b = businessman_with_customer_tuple[0]
    cs = businessman_with_customer_tuple[1]
    cs_ids = list(map(lambda e: e.id, cs))
    message = 'fake'
    used_for = SMSMessage.USED_FOR_CONTENT_MARKETING

    result = _send_plain(user=b, customers=cs, message=message, used_for=used_for)

    smsq = SMSMessage.objects.filter(
        businessman=b,
        message=message,
        used_for=used_for,
        message_type=SMSMessage.TYPE_PLAIN
    )

    receivers = SMSMessageReceivers.objects.filter(customer__id__in=cs_ids, sms_message=smsq.first())

    assert smsq.count() == 1
    assert smsq.first() == result
    assert receivers.count() == len(cs_ids)
    mock.assert_called_once_with(sms_message=result)


def test__set_receivers_for_sms_message_success(mocker, sms_message_pending_1, customers_list_1):
    mock = mock__set_reserved_credit_for_sms_message(mocker)

    _set_receivers_for_sms_message(sms=sms_message_pending_1, customers=customers_list_1)

    receivers = SMSMessageReceivers.objects.filter(customer__in=customers_list_1)
    assert receivers.count() == len(customers_list_1)


def test__set_reserved_credit_for_sms_message_success(mocker, sms_message_with_receivers):
    _set_reserved_credit_for_sms_message(sms_message=sms_message_with_receivers[0])

    expected_credit = len(sms_message_with_receivers[1]) * max_message_cost
    sms_message = SMSMessage.objects.get(id=sms_message_with_receivers[0].id)
    assert sms_message.reserved_credit == expected_credit
