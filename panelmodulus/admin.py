from django.contrib import admin
from .models import PanelModulus, BusinessmanModulus

# Register your models here.


class PanelModulusAdminModel(admin.ModelAdmin):

    list_display = ['name', 'cost']


class BusinessmanModulusAdminModel(admin.ModelAdmin):

    list_display = ['businessman', 'module', 'expire_at']


admin.site.register(PanelModulus, PanelModulusAdminModel)
admin.site.register(BusinessmanModulus, BusinessmanModulusAdminModel)
