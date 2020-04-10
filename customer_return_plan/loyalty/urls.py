from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoyaltySettingsRetrieveUpdateAPIVIew.as_view()),
]
