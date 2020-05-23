from django.urls import path, re_path
from . import views

urlpatterns = [
    path('templates/', views.SMSTemplateCreateListAPIView.as_view()),
    path('templates/<int:pk>/', views.SMSTemplateRetrieveAPIView.as_view()),
    path('send-sms/plain/', views.send_plain_sms),
    path('send-sms/plain/to-all/', views.send_plain_to_all),
    path('send-sms/plain/to-group/<int:group_id>/', views.send_plain_sms_to_group),
    path('resend-sms/<int:sms_id>/', views.resend_failed_sms),
    path('send-sms/template/<int:template_id>/', views.send_sms_by_template),
    path('send-sms/template/to-all/<int:template_id>/', views.send_sms_by_template_to_all),
    path('send-sms/template/<int:template_id>/to-group/<int:group_id>/', views.send_template_sms_to_group),
    path('resend-sms/template/<int:unsent_sms_id>/', views.resend_template_sms),

    path('failed/', views.FailedSMSMessagesList.as_view()),
    # path('unsent-sms/template/', views.list_unsent_template_sms),

    path('sent-sms/', views.get_businessman_sent_sms, name='sent_sms_retrieve')
]
