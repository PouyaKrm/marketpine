from base_app.error_codes import ApplicationErrorException
from base_app.tests import *
from panelprofile.models import SMSPanelInfo
# from smspanel.models import SMSMessage, SMSMessageReceivers
# from smspanel.services import send_plain_sms
from smspanel import services

from smspanel.models import SMSMessage, SMSMessageReceivers, SMSTemplate
from smspanel.services import send_by_template, send_by_template_to_all, send_plain_to_group, send_by_template_to_group, \
    resend_failed_message


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
