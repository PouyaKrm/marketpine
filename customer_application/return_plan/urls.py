from django.urls import path
from . import views

urlpatterns = [
    path('invite/', views.friend_invitation),
    path('discounts/', views.CustomerDiscountListAPIView.as_view()),
    path('discounts/<str:businessman_id>/', views.customer_businessman_discounts_list_api_view),
]
