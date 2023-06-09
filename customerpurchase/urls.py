from django.urls import path
from . import views

urlpatterns = [
    path('', views.PurchaseListCreateAPIView.as_view()),
    path('<int:purchase_id>/', views.CustomerPurchaseUpdateDeleteAPIView.as_view()),
    path('customer/<int:customer_id>/', views.get_customer_purchases),
]
