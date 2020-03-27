from .festivals import urls as festival_url
from .invitation import urls as invitation_url

from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_data),
    path('festival/', include(festival_url)),
    path('invitation/', include(invitation_url)),
    path('discounts/', views.DiscountListAPIView.as_view()),
    path('discounts/apply/', views.apply_discount),
    path('discounts/customer/<int:customer_id>/', views.CustomerDiscountsListAPIView.as_view())
]
