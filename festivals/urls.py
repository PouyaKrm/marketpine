from django.urls import path
from . import views

urlpatterns = [
    path('', views.FestivalAPIView.as_view()),
    path('<int:id>/', views.FestivalRetrieveAPIView.as_view()),
    path('<int:festival_id>/customers/', views.list_customers_in_festival),
    path('customers/', views.add_customer_to_festival),
    path('<int:festival_id>/customers/<customer_id>/', views.delete_customer_from_festival),
]