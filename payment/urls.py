from django.urls import path
from .views import *

app_name = "payment"

urlpatterns = [
    path('',create_payment,name="default_pay"),
    path('verify/', verify , name='verify'),
    path('activate/',create_constant_payment,name="activate_pay"),
    path('result/',ResultPay.as_view(),name="result_pay"),
    path('list/',ListPayView.as_view(),name="list_pay"),
    path('detail/<int:pk>',DetailPayView.as_view(),name="detail_pay"),
]
