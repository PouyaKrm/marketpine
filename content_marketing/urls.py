from django.urls import path
from .views import showvideo,VideoUploadView

app_name = "content_marketing"

urlpatterns = [
    path('showvideo/',showvideo , name='showvideo'),
    path('uploadvideo/',VideoUploadView.as_view(),name='uploadvideo'),
]
