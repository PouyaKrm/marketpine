from django.contrib import admin
from .models import SMSTemplate

# Register your models here.


class SMSTemplateAdmin(admin.ModelAdmin):

    list_display = ['title', 'businessman', 'create_date']


admin.site.register(SMSTemplate, SMSTemplateAdmin)
