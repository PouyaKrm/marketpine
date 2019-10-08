from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.upload_auth_docs),
    path('auth/doc/', views.get_auth_pdf_doc),
]
