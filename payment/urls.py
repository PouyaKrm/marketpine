from django.urls import path
from .views import *

app_name = "payment"

urlpatterns = [
    path('', ListPayView.as_view()),
    path('verify/', verify, name='verify'),
    path('sms-panel/', create_payment_sms_credit),
    path('panel-activation/plans/', PanelActivationPlansListAPIView.as_view()),
    path('panel-activate/', panel_activation_payment, name="constant_pay"),
]

