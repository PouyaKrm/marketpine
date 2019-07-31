from django.conf.urls import url
from django.urls import path, re_path
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    path('salesman/create/', views.create_user),
    path('salesman/verify/resend/<int:user_id>/', views.resend_verification_code),
    re_path(r'^salesman/verify/(?P<code>\d{5})/$', views.verify_user),
    path('salesman/login/', views.login_api_view),
    path('salesman/profile/', views.SalesmanRetrieveUpdateAPIView.as_view()),
    path('salesman/resetpassword/', views.reset_user_password),
    path('salesman/forgetpassword/', views.user_forget_password),
    path('salesman/profile/logo/', views.UploadRetrieveProfileImage.as_view()),

]
