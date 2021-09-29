from rest_framework import status

from base_app.integration_test_conf import *
from smspanel.serializers import SMSTemplateSerializer
from smspanel.tests.sms_panel_test_fixtures import *

pytestmark = pytest.mark.integration


def test_template_list(mocker, auth_client, sms_template_list):
    url = reverse('smspanel_templates')
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    sr = SMSTemplateSerializer(sms_template_list, many=True)
    d = sr.data
    assert all(e in response.data for e in d)
