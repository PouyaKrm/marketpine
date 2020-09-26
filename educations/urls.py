from django.urls import path
from . import views


urlpatterns = [
    path('', views.EducationsListAPIView.as_view())
]
