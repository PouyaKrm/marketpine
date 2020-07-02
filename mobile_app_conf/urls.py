from django.urls import path
from . import views

urlpatterns = [
    path('', views.MobileAppPageConfAPIView.as_view()),
    path('headers/', views.upload_header_image),
    path('headers/<int:id>/', views.MobileAppHeaderDeleteAPIView.as_view()),
]
