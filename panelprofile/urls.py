from django.urls import path
from . import views

urlpatterns = [
    path('', views.BusinessmanRetrieveUpdateProfileAPIView.as_view()),
    path('logo/', views.UploadRetrieveProfileImage.as_view()),
    path('<int:businessman_id>/logo/', views.get_user_logo),
    path('auth/authorize/', views.UploadBusinessmanDocs.as_view()),
]
