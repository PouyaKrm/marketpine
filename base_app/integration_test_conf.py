import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def auth_client(businessman_1):
    client = APIClient()
    password = '123'
    businessman_1.set_password(password)
    businessman_1.save()
    url = reverse('businessman_login')
    response = client.post(url, {'username': businessman_1.username, 'password': password})
    token = response.data['access_token']['token']
    client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
    return client
