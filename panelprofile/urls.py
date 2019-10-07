from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.take_authenticate_documents)
]
