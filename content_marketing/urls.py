from django.urls import path
from .views import *

app_name = "content_marketing"

urlpatterns = [
    path('post/', PostCreateListAPIView.as_view(), name='upload_post'),
    path('post/<int:post_id>/', PostRetrieveDeleteAPIView.as_view(), name='detail_post'),
    path('post/<int:post_id>/comments/', PostCommentListApiView.as_view()),
    # path('settings/', ContentMarketingSettingsCreateUpdateRetrieveAPIView.as_view())
    # path('post/<int:post_id>/comments/', detail_comment_post, name='detail_comment_post'),
    # path('post/comment/<int:post_id>/', set_comment_post, name='set_comment_post'),
    # path('post/<int:post_id>/likes/', detail_like_post, name='detail_like_post'),
    # path('post/like/<int:post_id>/', set_like_post, name='set_like_post'),
]

