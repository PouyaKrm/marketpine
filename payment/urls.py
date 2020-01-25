from django.urls import path
from .views import *

app_name = "payment"

urlpatterns = [
    path('', ListPayView.as_view()),
    path('verify/', verify, name='verify'),
    path('sms-panel/', create_payment_sms_credit),
    path('panel-activate/', create_constant_payment, name="constant_pay")

]

