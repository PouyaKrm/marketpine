from django.urls import path
from . import views

urlpatterns = [
    path('', views.RetrieveUpdatePanelSettingApiView.as_view()),
]
