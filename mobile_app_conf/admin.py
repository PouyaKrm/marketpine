from django.contrib import admin
from .models import MobileAppPageConf, MobileAppHeader

# Register your models here.

#
# class MobileAppPageConfAdminModel(admin.ModelAdmin):
#
#     list_display = ['businessman']


admin.site.register(MobileAppPageConf)
admin.site.register(MobileAppHeader)
