from django.contrib import admin
from .models import SMSTemplate, SentSMS, UnsentPlainSMS, UnsentTemplateSMS, SMSMessage, SMSMessageReceivers


# Register your models here.


class SMSTemplateAdmin(admin.ModelAdmin):

    list_display = ['title', 'businessman', 'create_date']


class SentSMSAdmin(admin.ModelAdmin):

    list_display = ['businessman', 'message_id', 'receptor']

class UnsentPLAINSMSAdmin(admin.ModelAdmin):

    list_display = ['businessman', 'message', 'create_date']

class UnsentTemplateSMSAdmin(admin.ModelAdmin):

    list_display = ['businessman', 'template', 'create_date']

admin.site.register(SMSTemplate, SMSTemplateAdmin)

admin.site.register(SentSMS, SentSMSAdmin)

admin.site.register(UnsentPlainSMS, UnsentPLAINSMSAdmin)

admin.site.register(UnsentTemplateSMS, UnsentTemplateSMSAdmin)

admin.site.register(SMSMessage)
admin.site.register(SMSMessageReceivers)
