from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.BusinessmanRetrieveUpdateProfileAPIView.as_view()),
    path('auth/authorize/', views.UploadBusinessmanDocs.as_view()),
    path('auth/doc/', views.get_auth_pdf_doc),
]
