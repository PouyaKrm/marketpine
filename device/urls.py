from django.urls import path
from .views import RegisterCustomer, InviteFriend  # ,register_customer

app_name = "Device"

urlpatterns = [
    # path('register/<int:imei_number>/', register_customer , name='register_customer'),
    path('register/<int:imei_number>/customer/', RegisterCustomer.as_view() , name='RegisterCustomer'),
    path('customer/', RegisterCustomer.as_view(), name='RegisterCustomer'),
    path('invite/', InviteFriend.as_view())
]
