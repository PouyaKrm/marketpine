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
from rest_framework_swagger.views import get_swagger_view

from users import urls as salesman_url, models
from customers import urls as customer_url
from groups import urls as group_url
from smspanel import urls as smspanel_url
from festivals import urls as festival_url
from invitation import urls as invitation_url
from dashboard import urls as dashboard_url
from customerpurchase import urls as purchase_url


schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include(salesman_url)),
    path('api/docs/', schema_view),
    path('api/salesman/customers/', include(customer_url)),
    path('api/salesman/customers/groups/', include(group_url)),
    path('api/salesman/smspanel/', include(smspanel_url)),
    path('api/salesman/festivals/', include(festival_url)),
    path('api/salesman/invitations/', include(invitation_url)),
    path('api/salesman/dashboard/', include(dashboard_url)),
    path('api/salesman/customer-purchase/', include(purchase_url)),
]


