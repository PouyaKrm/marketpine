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
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static

from smspanel.background_jobs.invitate_welcome_sms import run_send_invite_sms_task
from smspanel.background_jobs.sms_send_script import run_send_sms_task
from users import urls as salesman_url
from customers import urls as customer_url
from groups import urls as group_url
from smspanel import urls as smspanel_url
from customer_return_plan import urls as plan_url
from dashboard import urls as dashboard_url
from customerpurchase import urls as purchase_url
from panelmodulus import urls as modulus_url
from panelprofile import urls as profile_url
from download import urls as download_url
from payment import urls as payment_url
from device import urls as device_url
from content_marketing import urls as content_url
from online_menu import urls as menu_url
from mobile_app_conf import urls as mobile_conf_urls
from educations import urls as education_url

from customer_application import urls as customer_auth_urls

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include(salesman_url)),
    path('api/customers/', include(customer_auth_urls)),
    path('api/docs/', schema_view),
    path('api/salesman/customers/', include(customer_url)),
    path('api/salesman/customers/groups/', include(group_url)),
    path('api/salesman/smspanel/', include(smspanel_url)),
    path('api/salesman/plan/', include(plan_url)),
    path('api/salesman/dashboard/', include(dashboard_url)),
    path('api/salesman/customer-purchase/', include(purchase_url)),
    path('api/salesman/modulus/', include(modulus_url)),
    path('api/salesman/profile/', include(profile_url)),
    path('api/download/', include(download_url)),
    path('api/salesman/device/',include(device_url)),
    path('api/salesman/content/',include(content_url)),
    path('api/salesman/payment/', include(payment_url)),
    path('api/salesman/menu/', include(menu_url)),
    path('api/salesman/mobile-app/', include(mobile_conf_urls)),
    path('api/salesman/educations/', include(education_url))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# run_send_invite_sms_task(repeat=10)
# run_send_sms_task(repeat=10)
# BusinessCategory.create_default_categories()

run_send_invite_sms_task(repeat=10)
run_send_sms_task(repeat=10)
