from django.urls import path
from . import views

urlpatterns = [
 path('', views.PostsListAPIView.as_view()),
 path('<int:post_id>/', views.RetrievePost.as_view()),
]

