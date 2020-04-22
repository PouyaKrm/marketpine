from django.contrib import admin
from .models import PanelSetting
# Register your models here.


class PanelSettingAdminModel(admin.ModelAdmin):

    list_display = ['businessman', 'send_welcome_message', 'create_date', 'update_date']


admin.site.register(PanelSetting, PanelSettingAdminModel)
