from django.contrib import admin
from .models import FriendInvitation
# Register your models here.


class FriendInvitationAdminModel(admin.ModelAdmin):

    list_display = ['friend_phone', 'invited_by', 'invitation_date']


admin.site.register(FriendInvitation, FriendInvitationAdminModel)
