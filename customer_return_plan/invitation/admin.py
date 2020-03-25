from django.contrib import admin
from .models import FriendInvitation, FriendInvitationSettings
# Register your models here.


class FriendInvitationAdminModel(admin.ModelAdmin):

    list_display = ['id', 'businessman', 'inviter', 'invited']


admin.site.register(FriendInvitation, FriendInvitationAdminModel)
admin.site.register(FriendInvitationSettings)

