from django.urls import path
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    path('salesman/create/', views.create_user),
    path('salesman/login/', obtain_jwt_token),
    path('salesman/profile/', views.SalesmanAPIView.as_view()),
    path('salesman/resetpassword/', views.salesman_reset_password),

]
