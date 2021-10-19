from django.urls import path

from . import views

urlpatterns = [
    path('templates/', views.SMSTemplateList.as_view(), name='smspanel_templates'),
    path('templates/<int:template_id>/', views.SMSTemplateRetrieveAPIView.as_view(), name='sms_template_retrieve'),
    path('send-sms/plain/', views.SendPlainSms.as_view(), name='send_plain_sms'),
    path('send-sms/plain/to-all/', views.SendPlainToAllAPIView.as_view(), name='send_plain_sms_to_all'),
    path('send-sms/plain/to-group/<int:group_id>/', views.SendPlainSmsToGroupAPIView.as_view(),
         name='send_plain_sms_to_group'),
    path('resend-sms/<int:sms_id>/', views.ResendFailedSmsAPIView),
    path('send-sms/template/', views.SendByTemplateAPIView.as_view(), name='send_sms_by_template'),
    path('send-sms/template/to-all/<int:template_id>/', views.SendByTemplateToAll.as_view(),
         name='send_sms_by_template_to_all'),
    path('send-sms/template/<int:template_id>/to-group/<int:group_id>/', views.SendTemplateSmsToGroupAPIView.as_view(),
         name='send_sms_by_template_to_group'),
    # path('resend-sms/template/<int:unsent_sms_id>/', views.resend_template_sms),
    path('failed/', views.FailedSMSMessagesList.as_view(), name='failed_sms'),
    path('failed/<int:sms_id>/resend/', views.ResendFailedSmsAPIView.as_view(), name='resend_failed_sms'),
    path('sent-sms/', views.SentSMSListAPIView.as_view(), name='sent_sms_retrieve'),
    path('welcome-message/', views.RetrieveUpdateWelcomeMessageAPIView.as_view(), name='welcome_message'),
    # path('sent-sms/delivery-callback', views.DeliveryCallbackView.as_view(), name='sms_delivery_callback')
]
