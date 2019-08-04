from django.contrib import admin
from .models import PanelSetting
# Register your models here.


class PanelSettingAdminModel(admin.ModelAdmin):

    list_display = ['businessman']


admin.site.register(PanelSetting, PanelSettingAdminModel)