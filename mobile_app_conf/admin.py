from django.contrib import admin

from .forms import MobileAppPageConfForm
from .models import MobileAppPageConf, MobileAppHeader, ContactInfo


# Register your models here.


class MobileAppPageConfAdminModel(admin.ModelAdmin):

    list_display = ['businessman', 'create_date', 'update_date']
    form = MobileAppPageConfForm


class ContactInfoAdminModel(admin.ModelAdmin):

    list_display = ['phone']


admin.site.register(MobileAppPageConf, MobileAppPageConfAdminModel)
admin.site.register(MobileAppHeader)
admin.site.register(ContactInfo, ContactInfoAdminModel)
