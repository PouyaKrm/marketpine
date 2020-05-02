from django.contrib import admin
from .models import BusinessmanGroups
from .forms import AddGroupForm

# Register your models here.
class BusinessmanGroupsAdminModel(admin.ModelAdmin):

    list_display = ['title', 'type', 'businessman', 'create_date']
    form = AddGroupForm

admin.site.register(BusinessmanGroups, BusinessmanGroupsAdminModel)
