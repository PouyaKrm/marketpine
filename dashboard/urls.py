from django.urls import path
from . import views


urlpatterns = [
    path('customers/', views.customers_total),
    path('customers/top/', views.get_top_5_customers),
]
