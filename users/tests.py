from django.test import TestCase
from rest_framework.test import APIRequestFactory
from . import views
# Create your tests here.

factory  = APIRequestFactory()

request = factory.post('/salesperson/create/', {'username': 'jack'}, format='json')

data = views.create_user(request)

print(data)
