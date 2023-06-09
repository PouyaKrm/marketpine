from django.contrib import admin
from .models import SMSTemplate, SentSMS, UnsentPlainSMS, UnsentTemplateSMS, SMSMessage, SMSMessageReceivers, \
    WelcomeMessage
from .forms import SMSMessageForm

# Register your models here.


class SMSTemplateAdmin(admin.ModelAdmin):

    list_display = ['title', 'businessman', 'create_date']


class SMSMessageAdminModel(admin.ModelAdmin):
    list_display = ['businessman', 'status', 'create_date']
    form = SMSMessageForm


class SentSMSAdmin(admin.ModelAdmin):

    list_display = ['sms_message', 'message_id', 'receptor', 'create_date']


class UnsentPLAINSMSAdmin(admin.ModelAdmin):

    list_display = ['businessman', 'message', 'create_date']


class UnsentTemplateSMSAdmin(admin.ModelAdmin):

    list_display = ['businessman', 'template', 'create_date']


class WelcomeMessageAdminModel(admin.ModelAdmin):

    list_display = ['message', 'send_message']


admin.site.register(SMSTemplate, SMSTemplateAdmin)

admin.site.register(SentSMS, SentSMSAdmin)

admin.site.register(UnsentPlainSMS, UnsentPLAINSMSAdmin)

admin.site.register(UnsentTemplateSMS, UnsentTemplateSMSAdmin)

admin.site.register(SMSMessage, SMSMessageAdminModel)
admin.site.register(SMSMessageReceivers)
admin.site.register(WelcomeMessage, WelcomeMessageAdminModel)
