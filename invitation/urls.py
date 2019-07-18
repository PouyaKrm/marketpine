from django.urls import path
from . import views

urlpatterns = [
    path('bot/', views.FriendInvitationListAPIView.as_view()),
    path('', views.list_friend_invitation_businessman),
    path('<int:invitation_id>/', views.friend_invitation_retrieve),

]
