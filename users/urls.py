from django.urls import path
from . import views
from django.urls import path

from . import views

urlpatterns = [
    path('salesman/create/', views.create_user),
    # path('salesman/verify/resend/<int:user_id>/', views.resend_verification_code),
    # re_path(r'^salesman/verify/(?P<businessman_id>\d+)/(?P<code>\d{5})/$', views.verify_user),
    path('salesman/login/', views.login_api_view, name='businessman_login'),
    path('salesman/refresh/', views.get_access_token),
    path('salesman/resetpassword/', views.reset_user_password),
    path('salesman/forgetpassword/', views.user_forget_password),
    path('salesman/categories/', views.get_top5_categories_and_username_phone_email_exists),
    path('salesman/exists/', views.exists)
]
