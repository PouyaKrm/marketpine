from django.urls import path
from . import views
urlpatterns = [
    path('', views.BusinessmanCustomerListAPIView.as_view()),
    path('<int:customer_id>/', views.BusinessmanCustomerRetrieveAPIView.as_view()),
]
