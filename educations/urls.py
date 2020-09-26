from django.urls import path
from . import views


urlpatterns = [
    path('', views.EducationsListAPIView.as_view()),
    path('types/', views.get_education_type_list)
]
