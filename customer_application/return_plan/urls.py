from django.urls import path

from . import views

urlpatterns = [
    path('invite/', views.friend_invitation),
    path('discounts/', views.CustomerDiscountListAPIView.as_view()),
]
