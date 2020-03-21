from django.urls import path
from . import views

urlpatterns = [
    path('bot/', views.FriendInvitationListAPIView.as_view()),
    path('', views.BusinessmanInvitationListAPIView.as_view()),
    path('<int:invitation_id>/', views.friend_invitation_retrieve),
    path('settings/', views.FriendInvitationSettingAPIView.as_view())

]
