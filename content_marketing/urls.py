from django.urls import path
from .views import PostUploadView,detailpost,detail_comment_post

app_name = "content_marketing"

urlpatterns = [
    # path('showpost/',showpost , name='showpost'),
    path('post/upload/',PostUploadView.as_view(),name='upload_post'),
    path('post/<int:post_id>/',detailpost,name='detail_post'),
    path('post/<int:post_id>/comment/',detail_comment_post,name='comment_post'),
]
