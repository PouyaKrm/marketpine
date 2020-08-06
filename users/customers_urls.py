from django.urls import path
from . import customers_views

urlpatterns = [
    path('login/send-code/', customers_views.send_login_code),
    path('login/', customers_views.customer_login)
]
