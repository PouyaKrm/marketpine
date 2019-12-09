from django.urls import path, re_path
from . import views

urlpatterns = [
    path('templates/', views.SMSTemplateCreateListAPIView.as_view()),
    path('templates/<int:pk>/', views.SMSTemplateRetrieveAPIView.as_view()),
    path('send-sms/plain/', views.send_plain_sms),
    path('send-sms/plain/to-all/', views.send_plain_to_all),
    path('send-sms/template/<int:template_id>/', views.send_sms_by_template),
    path('send-sms/template/to-all/<int:template_id>/', views.send_sms_by_template_to_all),
    path('sent-sms/', views.get_businessman_sent_sms),
    path('sent-sms/customer/<int:customer_id>/', views.get_customer_sent_sms),
]
