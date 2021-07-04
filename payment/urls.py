from django.urls import path

from .views import *

app_name = "payment"

urlpatterns = [
    path('', ListPayView.as_view()),
    path('verify/', VerifyPayment.as_view(), name='verify'),
    path('sms-panel/', create_payment_sms_credit),
    path('panel-activation/plans/', PanelActivationPlansListAPIView.as_view()),
    path('panel-activation/activate/', panel_activation_payment, name="constant_pay"),
    path('billing/', BillingSummeryAPIView.as_view())
]
