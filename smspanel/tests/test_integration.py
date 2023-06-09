from django.conf import settings
from rest_framework import status

from base_app.integration_test_conf import *
from base_app.test_utils import get_model_list_ids
from common.util.sms_panel.client import ClientManagement
from panelprofile.serializers import SMSPanelInfoSerializer
from smspanel.serializers import SMSTemplateSerializer, SMSMessageListSerializer, SentSMSSerializer, \
    WelcomeMessageSerializer
from smspanel.tests.sms_panel_test_fixtures import *
from groups.tests.fixtures import group_1, group_1_customer_tuple

message_cost = settings.SMS_PANEL['MAX_MESSAGE_COST']

pytestmark = pytest.mark.integration


@pytest.fixture
def sms_fetch_user_api_key_mock(mocker):
    return mocker.patch.object(ClientManagement, 'fetch_user_by_api_key', return_value=get_sms_panel_info_object())


def mock_fetch_panel_profile(mocker, sms_panel_info):
    return mocker.patch('panelprofile.services.sms_client_management.fetch_user_by_api_key',
                        return_value=sms_panel_info)


def assert_sms_panel_info(response_data, sms_panel_model: SMSPanelInfo):
    sr = SMSPanelInfoSerializer(sms_panel_model)
    assert response_data == sr.data


def get_last_customer_sorted_by_id(customers: List[Customer]) -> Customer:
    return sorted(customers, key=lambda e: e.id)[-1]


def assert_sms_message_reserved_credit(sms_message: SMSMessage, receivers_count: int):
    assert sms_message.reserved_credit == receivers_count * max_message_const


def test_template_list(mocker, auth_client, sms_template_list):
    url = reverse('smspanel_templates')
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    sr = SMSTemplateSerializer(sms_template_list, many=True)
    d = sr.data
    assert all(e in response.data for e in d)


def test_create_sms_template(mocker, auth_client, active_sms_panel_info_1, businessman_1):
    mock_fetch_panel_profile(mocker, active_sms_panel_info_1)
    url = reverse('smspanel_templates')
    title = 'title'
    content = 'content whatsup'
    response = auth_client.post(url, {'title': title, 'content': content})

    assert response.status_code == status.HTTP_200_OK
    q = SMSTemplate.objects.filter(businessman=businessman_1, title=title, content=content)
    assert q.exists()
    d = SMSTemplateSerializer(q.first()).data
    assert response.data == d


def test_retrieve_sms_template(mocker, auth_client, sms_template_1, active_sms_panel_info_1):
    mock_fetch_panel_profile(mocker, active_sms_panel_info_1)
    url = reverse('sms_template_retrieve', kwargs={'template_id': sms_template_1.id})

    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    sr = SMSTemplateSerializer(sms_template_1)
    assert response.data == sr.data


def test_update_sms_template(mocker, auth_client, sms_template_1, active_sms_panel_info_1):
    mock_fetch_panel_profile(mocker, active_sms_panel_info_1)
    t_id = sms_template_1.id
    url = reverse('sms_template_retrieve', kwargs={'template_id': t_id})
    title = fake.text()[:20].strip()
    content = fake.text()[:20].strip()

    response = auth_client.put(url, {'title': title, 'content': content}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == t_id
    assert response.data['title'] == title
    assert response.data['content'] == content
    assert SMSTemplate.objects.filter(id=t_id, title=title, content=content).exists()


def test_delete_sms_template(mocker, sms_fetch_user_api_key_mock, auth_client, sms_template_1, active_sms_panel_info_1):
    url = reverse('sms_template_retrieve', kwargs={'template_id': sms_template_1.id})

    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert not SMSTemplate.objects.filter(id=sms_template_1.id).exists()
    sr = SMSTemplateSerializer(sms_template_1)
    assert response.data == sr.data


def test_send_plain_sms(sms_fetch_user_api_key_mock, businessman_1_with_customer_tuple, active_sms_panel_info_1,
                        auth_client):
    url = reverse('send_plain_sms')
    customer_ids = list(map(lambda e: e.id, businessman_1_with_customer_tuple[1]))
    message = 'test message'

    response = auth_client.post(url, data={'customers': customer_ids, 'content': message})

    assert response.status_code == status.HTTP_200_OK
    smsq = SMSMessage.objects.filter(message=message, message_type=SMSMessage.TYPE_PLAIN,
                                     businessman=businessman_1_with_customer_tuple[0])
    assert smsq.exists()
    sms = smsq.first()
    receivers_count = SMSMessageReceivers.objects.filter(customer_id__in=customer_ids, sms_message=sms).count()
    assert receivers_count == len(customer_ids)
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
    assert_sms_message_reserved_credit(sms, receivers_count)


def test_send_plain_to_all(sms_fetch_user_api_key_mock, businessman_1_with_customer_tuple, active_sms_panel_info_1,
                           auth_client):
    url = reverse('send_plain_sms_to_all')
    message = 'test message'
    last_id = get_last_customer_sorted_by_id(businessman_1_with_customer_tuple[1]).id

    response = auth_client.post(url, data={'content': message})

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(businessman=businessman_1_with_customer_tuple[0],
                                      message_type=SMSMessage.TYPE_PLAIN,
                                      message=message)

    assert sms_q.exists()
    assert sms_q.first().last_receiver_id == last_id
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
    assert_sms_message_reserved_credit(sms_q.first(), last_id)


def test_send_template_sms(sms_fetch_user_api_key_mock, sms_template_1, businessman_1_with_customer_tuple,
                           active_sms_panel_info_1, auth_client):
    url = reverse('send_sms_by_template')
    customer_ids = get_model_list_ids(businessman_1_with_customer_tuple[1])

    response = auth_client.post(url, data={'customers': customer_ids, 'template': sms_template_1.id})

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(businessman=businessman_1_with_customer_tuple[0],
                                      message_type=SMSMessage.TYPE_TEMPLATE,
                                      message=sms_template_1.content
                                      )

    assert sms_q.exists()
    receivers_count = SMSMessageReceivers.objects.filter(sms_message=sms_q.first(),
                                                         customer_id__in=customer_ids).count()
    assert receivers_count == len(customer_ids)
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
    assert_sms_message_reserved_credit(sms_q.first(), receivers_count)


def test_send_by_template_to_all(sms_fetch_user_api_key_mock, businessman_1_with_customer_tuple, sms_template_1,
                                 active_sms_panel_info_1, auth_client):
    url = reverse('send_sms_by_template_to_all', kwargs={'template_id': sms_template_1.id})
    last_id = get_last_customer_sorted_by_id(businessman_1_with_customer_tuple[1]).id

    response = auth_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(businessman=businessman_1_with_customer_tuple[0],
                                      message=sms_template_1.content,
                                      message_type=SMSMessage.TYPE_TEMPLATE,
                                      last_receiver_id=last_id
                                      )

    assert sms_q.exists()
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
    assert_sms_message_reserved_credit(sms_q.first(), last_id)


def test_send_plain_sms_to_group(sms_fetch_user_api_key_mock, group_1_customer_tuple, active_sms_panel_info_1,
                                 auth_client):
    g = group_1_customer_tuple[0]
    customers = group_1_customer_tuple[1]
    customers_count = len(group_1_customer_tuple[1])
    last_id = get_last_customer_sorted_by_id(group_1_customer_tuple[1]).id
    url = reverse('send_plain_sms_to_group', kwargs={'group_id': g.id})
    message = 'fake message'

    response = auth_client.post(url, data={'content': message})

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(
        businessman=g.businessman,
        message=message,
        message_type=SMSMessage.TYPE_PLAIN,
        last_receiver_id=last_id
    )
    assert sms_q.exists()
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
    assert_sms_message_reserved_credit(sms_q.first(), customers_count)


def test_send_template_sms_to_group(sms_fetch_user_api_key_mock, group_1_customer_tuple, sms_template_1,
                                    active_sms_panel_info_1, auth_client):
    g = group_1_customer_tuple[0]
    customers = group_1_customer_tuple[1]
    customers_count = len(customers)
    last_id = get_last_customer_sorted_by_id(customers).id

    url = reverse('send_sms_by_template_to_group', kwargs={'template_id': sms_template_1.id, 'group_id': g.id})

    response = auth_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(businessman=g.businessman, message_type=SMSMessage.TYPE_TEMPLATE,
                                      message=sms_template_1.content,
                                      last_receiver_id=last_id
                                      )
    assert sms_q.exists()
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
    assert_sms_message_reserved_credit(sms_q.first(), customers_count)


def test_failed_sms_list(sms_fetch_user_api_key_mock, sms_message_failed_list_1, active_sms_panel_info_1, auth_client):
    url = reverse('failed_sms')

    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    result = response.data['results']
    expected = SMSMessageListSerializer(sms_message_failed_list_1, many=True).data
    assert all(e in result for e in expected)


def test_resend_failed_sms(sms_fetch_user_api_key_mock, sms_message_failed_list_1, active_sms_panel_info_1,
                           auth_client):
    sms = sms_message_failed_list_1[0]
    url = reverse('resend_failed_sms', kwargs={'sms_id': sms.id})

    response = auth_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(id=sms.id, status=SMSMessage.STATUS_DONE, send_fail_attempts=0)
    assert sms_q.exists()
    assert_sms_panel_info(response.data, active_sms_panel_info_1)


def test_sent_sms_list(sms_fetch_user_api_key_mock, sent_sms_list_1, active_sms_panel_info_1, auth_client):
    url = reverse('sent_sms_retrieve')

    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    result = response.data['results']
    expected = SentSMSSerializer(sent_sms_list_1, many=True).data
    assert all(e in result for e in expected)


def test_retrieve_welcome_message(sms_fetch_user_api_key_mock, welcome_message_1, active_sms_panel_info_1, auth_client):
    url = reverse('welcome_message')

    response = auth_client.get(url)

    sr = WelcomeMessageSerializer(welcome_message_1)
    assert response.data == sr.data


def test_update_welcome_message(sms_fetch_user_api_key_mock, active_sms_panel_info_1, auth_client):
    data = {'message': 'fake message', 'send_message': True}
    url = reverse('welcome_message')

    response = auth_client.put(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    query = WelcomeMessage.objects.filter(businessman=active_sms_panel_info_1.businessman, **data)
    assert query.exists()
    result = response.data
    assert data.items() <= result.items()


def test_deliver_callback(sent_sms_list_1):
    sent_sms = sent_sms_list_1[0]
    new_status = 100
    client = APIClient()
    data = {'messageid': sent_sms.message_id, 'status': new_status}
    url = reverse('sms_delivery_callback')

    response = client.post(url, data=data, format='multipart')

    assert response.status_code == status.HTTP_200_OK
    sent_sms = SentSMS.objects.get(message_id=sent_sms.message_id)
    assert sent_sms.status == new_status
