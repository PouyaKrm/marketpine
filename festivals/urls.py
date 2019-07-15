from django.urls import path
from . import views

urlpatterns = [
    path('', views.FestivalAPIView.as_view()),
    path('<int:id>/', views.FestivalRetrieveAPIView.as_view()),
]