from django.contrib import admin
from .models import SMSTemplate, SentSMS


# Register your models here.


class SMSTemplateAdmin(admin.ModelAdmin):

    list_display = ['title', 'businessman', 'create_date']


class SentSMSAdmin(admin.ModelAdmin):

    list_display = ['businessman', 'sent_date']


admin.site.register(SMSTemplate, SMSTemplateAdmin)

admin.site.register(SentSMS, SentSMSAdmin)
