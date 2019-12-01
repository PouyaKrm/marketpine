from django.urls import path
from .views import *

app_name = "payment"

urlpatterns = [
    path('verify/', verify , name='verify'),
    path('default_pay/',create_payment,name="default_pay"),
    path('constant_pay/',create_constant_payment,name="constant_pay"),
    path('result_pay/',ResultPay.as_view(),name="result_pay"),
]
