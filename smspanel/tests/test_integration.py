from rest_framework import status

from base_app.integration_test_conf import *
from common.util.sms_panel.client import ClientManagement
from panelprofile.serializers import SMSPanelInfoSerializer
from smspanel.serializers import SMSTemplateSerializer
from smspanel.tests.sms_panel_test_fixtures import *

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
    receivers_q = SMSMessageReceivers.objects.filter(customer_id__in=customer_ids, sms_message=sms)
    assert receivers_q.count() == len(customer_ids)
    assert_sms_panel_info(response.data, active_sms_panel_info_1)


def test_send_plain_to_all(sms_fetch_user_api_key_mock, businessman_1_with_customer_tuple, active_sms_panel_info_1,
                           auth_client):
    url = reverse('send_plain_sms_to_all')
    message = 'test message'

    response = auth_client.post(url, data={'content': message})

    assert response.status_code == status.HTTP_200_OK
    sms_q = SMSMessage.objects.filter(businessman=businessman_1_with_customer_tuple[0],
                                      message_type=SMSMessage.TYPE_PLAIN,
                                      message=message)
    assert sms_q.exists()
    receivers_q = SMSMessageReceivers.objects.filter(sms_message=sms_q.first(),
                                                     customer__businessmans=businessman_1_with_customer_tuple[0])
    assert receivers_q.count() == len(businessman_1_with_customer_tuple[1])
    assert_sms_panel_info(response.data, active_sms_panel_info_1)
