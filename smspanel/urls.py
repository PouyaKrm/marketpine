from django.urls import path, re_path
from . import views

urlpatterns = [
    path('templates/', views.SMSTemplateCreateListAPIView.as_view()),
    path('templates/<int:pk>/', views.SMSTemplateRetrieveAPIView.as_view()),
    path('send-sms/plain/', views.send_plain_sms),
    path(r'send-sms/template/<int:template_id>/', views.send_sms_by_template),
]
