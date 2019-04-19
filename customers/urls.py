from django.urls import path
from . import views
urlpatterns = [
    path('', views.SalesmanCustomerListAPIView.as_view()),
     path('<int:pk>/', views.SalesmanCustomerRetrieveAPIView.as_view()),

]