from django.urls import path
from . import views

urlpatterns = [
    path('', views.FestivalAPIView.as_view()),
    path('<int:id>/', views.FestivalRetrieveAPIView.as_view()),
    path('by-code/<str:discount_code>/', views.get_festival_by_discount_code),
    path('<int:festival_id>/customers/', views.list_customers_in_festival),
    path('customers/', views.add_customer_to_festival),
    path('<int:festival_id>/customers/<customer_id>/', views.delete_customer_from_festival),
    path('exists/', views.check_festival_name_or_discount_code_exists),
]
