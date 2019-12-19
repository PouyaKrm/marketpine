from django.urls import path
from .views import *

app_name = "content_marketing"

urlpatterns = [
    # path('showpost/',showpost , name='showpost'),
    path('post/upload/',PostUploadView.as_view(),name='upload_post'),
    path('post/<int:post_id>/',detailpost,name='detail_post'),
    path('post/<int:post_id>/comments/',detail_comment_post,name='detail_comment_post'),
    path('post/comment/<int:post_id>/',set_comment_post,name='set_comment_post'),
    path('post/<int:post_id>/likes/',detail_like_post,name='detail_like_post'),
    path('post/like/<int:post_id>/',set_like_post,name='set_like_post'),
]
