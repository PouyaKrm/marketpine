from django.urls import path
from . import views

urlpatterns = [
    path('', views.MobileAppPageConfAPIView.as_view())
]
