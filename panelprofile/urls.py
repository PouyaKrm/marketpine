from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('auth/(?P<doc_type>(form|card|certificate))/', views.upload_auth_docs),
    path('auth/authenticate/', views.authenticate_user),
    path('auth/doc/', views.get_auth_pdf_doc),
]
