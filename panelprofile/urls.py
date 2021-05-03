from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.BusinessmanRetrieveUpdateProfileAPIView.as_view()),
    path('logo/', views.UploadRetrieveProfileImage.as_view()),
    path('phone/verify/', views.SendPhoneVerificationCode.as_view()),
    path('phone/verify/resend/<int:verification_code_id>/', views.ResendVerificationCode.as_view()),
    re_path(r'^phone/verify/(?P<verification_code_id>\d+)/(?P<code>\d{5})/$', views.VerifyPhone.as_view()),
    path('phone/change/', views.PhoneChangeSendVerification.as_view()),
    path('phone/change/resend/<int:phone_chane_verification_id>/', views.PhoneChangeResend.as_view()),
    re_path(
        'phone/change/verify/(?P<phone_change_verification_id>\d+)/(?P<previous_phone_code>\d{5})/(?P<new_phone_code>\d{5})',
        views.PhoneChangeVerify.as_view()),
    path('<int:businessman_id>/logo/', views.get_user_logo),
    path('auth/authorize/', views.UploadBusinessmanDocs.as_view()),
]
