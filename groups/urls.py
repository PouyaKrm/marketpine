from django.conf.urls import url
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.BusinessmanGroupsListCreateAPIView.as_view()),
    path('<int:id>/', views.BusinessmanGroupsUpdateAPIView.as_view()),
    path('<int:group_id>/members/', views.GroupMembersAPIView.as_view())

]
