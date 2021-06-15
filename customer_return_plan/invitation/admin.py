from django.contrib import admin

from .forms import CreateChangeInvitationForm
from .models import FriendInvitation, FriendInvitationSettings


# Register your models here.


class FriendInvitationAdminModel(admin.ModelAdmin):
    list_display = ['id', 'businessman', 'inviter', 'invited']
    form = CreateChangeInvitationForm


admin.site.register(FriendInvitation, FriendInvitationAdminModel)
admin.site.register(FriendInvitationSettings)

