from django.urls import path
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    path('create/', views.create_user),
    path('login/', obtain_jwt_token),
    path('profile/', views.SalesmanAPIView.as_view()),
    path('resetpassword/', views.salesman_reset_password),

]
