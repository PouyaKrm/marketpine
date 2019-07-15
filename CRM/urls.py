"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from faker import Faker

from users import urls as salesman_url, models
from customers import urls as customer_url
from groups import urls as group_url
from smspanel import urls as smspanel_url

import schedule

from users import tasks

from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title="CRM API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include(salesman_url)),
    path('api/docs/', schema_view),
    # path('docs2/', schema_view),
    path('api/salesman/customers/', include(customer_url)),
    path('api/salesman/customers/groups/', include(group_url)),
    path('api/salesman/smspanel/', include(smspanel_url)),
]


# print('tasks run')
# tasks.generate_fake_businessman()
# schedule.every(20).seconds.do(tasks.delete_unverified_businessmans)
