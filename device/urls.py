from django.urls import path
from .views import register_customer,RegisterCustomer

app_name = "Device"

urlpatterns = [
    path('register_customer/<int:imei_number>/<int:phone_customer>/', register_customer , name='register_customer'),
    path('register/<int:imei_number>/<int:phone_customer>/', RegisterCustomer.as_view() , name='RegisterCustomer'),

]
