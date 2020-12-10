from django.urls import path
from . import views


urlpatterns = [
    path('customers/', views.customers_total),
    path('customers/top/', views.get_top_5_customers),
    path('purchase/week/', views.total_amount_days_in_week),
    path('', views.DashboardAPIView.as_view())
]
