from django.contrib import admin
from .models import MobileAppPageConf, MobileAppHeader, ContactInfo


# Register your models here.

#
# class MobileAppPageConfAdminModel(admin.ModelAdmin):
#
#     list_display = ['businessman']


class ContactInfoAdminModel(admin.ModelAdmin):

    list_display = ['phone']


admin.site.register(MobileAppPageConf)
admin.site.register(MobileAppHeader)
admin.site.register(ContactInfo, ContactInfoAdminModel)
