from django.urls import path

from . import views

urlpatterns = [
    path('templates/', views.SMSTemplateList.as_view(), name='smspanel_templates'),
    path('templates/<int:pk>/', views.SMSTemplateRetrieveAPIView.as_view()),
    path('send-sms/plain/', views.SendPlainSms.as_view()),
    path('send-sms/plain/to-all/', views.SendPlainToAllAPIView.as_view()),
    path('send-sms/plain/to-group/<int:group_id>/', views.SendPlainSmsToGroup.as_view()),
    path('resend-sms/<int:sms_id>/', views.ResendFailedSms),
    path('send-sms/template/', views.SendByTemplateAPIView.as_view()),
    path('send-sms/template/to-all/<int:template_id>/', views.SendByTemplateToAll.as_view()),
    path('send-sms/template/<int:template_id>/to-group/<int:group_id>/', views.SendTemplateSmsToGroup.as_view()),
    # path('resend-sms/template/<int:unsent_sms_id>/', views.resend_template_sms),
    path('failed/', views.FailedSMSMessagesList.as_view()),
    path('failed/<int:sms_id>/resend/', views.ResendFailedSms.as_view()),
    path('sent-sms/', views.SentSMSRetrieveAPIView.as_view(), name='sent_sms_retrieve'),
    path('welcome-message/', views.RetrieveUpdateWelcomeMessageApiView.as_view()),
]

