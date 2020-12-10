from django.urls import path
from . import views


urlpatterns = [
    path('', views.DashboardAPIView.as_view())
]
