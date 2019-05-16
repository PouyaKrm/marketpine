from django.conf.urls import url
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.BusinessmanGroupsListAPIView.as_view()),
    path('<int:id>/', views.BusinessmanGroupsUpdateAPIView.as_view()),
    path('<int:group_id>/members/', views.CustomerGroupRetrieveAPIView.as_view()),

]