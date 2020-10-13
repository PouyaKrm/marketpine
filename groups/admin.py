from django.contrib import admin
from .models import BusinessmanGroups, Membership
from .forms import AddGroupForm


class BusinessmanGroupsAdminModel(admin.ModelAdmin):

    list_display = ['title', 'type', 'businessman', 'create_date']
    form = AddGroupForm


class MembershipAdminModel(admin.ModelAdmin):
    list_display = ['group', 'customer', 'create_date']


admin.site.register(BusinessmanGroups, BusinessmanGroupsAdminModel)
admin.site.register(Membership, MembershipAdminModel)
