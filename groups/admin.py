from django.contrib import admin
from .models import BusinessmanGroups

# Register your models here.
class BusinessmanGroupsAdminModel(admin.ModelAdmin):

    list_display = ['title', 'businessman', 'create_date']

admin.site.register(BusinessmanGroups, BusinessmanGroupsAdminModel)
