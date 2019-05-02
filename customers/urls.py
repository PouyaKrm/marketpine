from django.urls import path
from . import views
urlpatterns = [
    path('', views.BusinessmanCustomerListAPIView.as_view()),
     path('<int:pk>/', views.BusinessmanCustomerRetrieveAPIView.as_view()),

]