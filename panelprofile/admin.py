from django.contrib import admin
from .models import SMSPanelInfo

# Register your models here.

class SMSPanelInfoAdmin(admin.ModelAdmin):

    list_display = ['username', 'status', 'credit']


admin.site.register(SMSPanelInfo, SMSPanelInfoAdmin)
