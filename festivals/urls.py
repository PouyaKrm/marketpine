from django.urls import path
from . import views

urlpatterns = [
    path('', views.FestivalAPIView.as_view()),
]