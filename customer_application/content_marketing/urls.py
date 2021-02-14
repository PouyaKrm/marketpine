from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostsListAPIView.as_view()),
    path('<int:post_id>/', views.PostRetrieveLikeAPIView.as_view()),
    path('<int:post_id>/like/', views.PostLike.as_view()),
    path('<int:post_id>/comments/', views.CommentsListCreateAPIView.as_view()),
]
