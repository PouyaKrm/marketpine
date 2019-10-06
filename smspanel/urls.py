from django.urls import path, re_path
from . import views

urlpatterns = [
    path('templates/', views.SMSTemplateCreateListAPIView.as_view()),
    path('templates/<int:pk>/', views.SMSTemplateRetrieveAPIView.as_view()),
    path('send-sms/plain/', views.send_plain_sms),
    path('send-sms/template/<int:template_id>/', views.send_sms_by_template),
    path('sent-sms/', views.get_businessman_sent_sms),
    path('sent-sms/customer/<int:customer_id>/', views.get_customer_sent_sms),
]
