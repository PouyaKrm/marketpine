from django.urls import path

from .views import *

app_name = "payment"

urlpatterns = [
    path('', ListPayView.as_view()),
    path('verify/', VerifyPayment.as_view(), name='verify'),
    path('sms-panel/', create_payment_sms_credit),
    path('wallet/', WalletCreditPaymentCreation.as_view()),
    path('subscription/', SubscriptionPaymentCreate.as_view()),
    path('billing/', BillingSummeryAPIView.as_view())
]
