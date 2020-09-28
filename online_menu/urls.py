from django.urls import path
from . import views

urlpatterns = [
    path('', views.OnlineMenuAPIView.as_view()),
    path('<int:menu_id>/', views.OnlineMenuRetrieveDeleteAPIView.as_view())
]
