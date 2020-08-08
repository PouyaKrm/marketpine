from django.urls import path
from customer_application import views

urlpatterns = [
    path('login/send-code/', views.send_login_code),
    path('login/', views.customer_login)
]
