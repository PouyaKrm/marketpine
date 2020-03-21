from django.contrib import admin
from .models import FriendInvitation, FriendInvitationDiscount, FriendInvitationSettings
# Register your models here.


class FriendInvitationAdminModel(admin.ModelAdmin):

    list_display = ['id', 'businessman', 'invited', 'inviter', 'invitation_date']


class FriendInvitationDiscountAdminModel(admin.ModelAdmin):
    list_display = ['discount_code', 'customer', 'role', 'friend_invitation']


admin.site.register(FriendInvitation, FriendInvitationAdminModel)
admin.site.register(FriendInvitationDiscount, FriendInvitationDiscountAdminModel)
admin.site.register(FriendInvitationSettings)

