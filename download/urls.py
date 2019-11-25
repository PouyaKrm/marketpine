from django.urls import path, include

from .profiledownload import urls as profile_url

urlpatterns = [
    path('profile/', include(profile_url))
]
