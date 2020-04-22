from django.urls import path
from . import views

urlpatterns = [
    path('', views.OnlineMenuAPIView.as_view()),
]
