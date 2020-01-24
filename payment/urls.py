from django.urls import path
from .views import *

app_name = "payment"

urlpatterns = [
<<<<<<< HEAD
    path('verify/', verify, name='verify'),
    path('sms-panel/', create_payment_sms_credit),
    path('panel-activate/', create_constant_payment, name="constant_pay"),
    path('result_pay/', ResultPay.as_view(), name="result_pay"),
=======
    path('',create_payment,name="default_pay"),
    path('verify/', verify , name='verify'),
    path('activate/',create_constant_payment,name="activate_pay"),
    path('result/',ResultPay.as_view(),name="result_pay"),
    path('list/',ListPayView.as_view(),name="list_pay"),
    path('detail/<int:pk>',DetailPayView.as_view(),name="detail_pay"),
>>>>>>> 966c21bb2f3eaaf1820cec3c460ff4545f6ac077
]
