from django.contrib import admin
from .models import FriendInvitation, FriendInviterDiscount, InvitedFriendDiscount
# Register your models here.


class FriendInvitationAdminModel(admin.ModelAdmin):

    list_display = ['id', 'businessman', 'invited', 'inviter', 'invitation_date']


class InvitedFriendDiscountAdmin(admin.ModelAdmin):
    list_display = ['discount_code', 'invited', 'friend_invitation']


class FriendInviterDiscountAdmin(admin.ModelAdmin):
    list_display = ['discount_code', 'inviter', 'friend_invitation']


admin.site.register(FriendInvitation, FriendInvitationAdminModel)
admin.site.register(FriendInviterDiscount, FriendInviterDiscountAdmin)
admin.site.register(InvitedFriendDiscount, InvitedFriendDiscountAdmin)
