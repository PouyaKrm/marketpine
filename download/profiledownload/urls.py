from django.urls import path, re_path

from . import views

urlpatterns = [
    path('logo/', views.download_logo),
    re_path(r'^auth-doc/(?P<file_type>\w+)/$', views.download_auth_docs)
]
