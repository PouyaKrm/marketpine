from django.contrib import admin
from .models import Device

class DeviceAdmin(admin.ModelAdmin):
    fields = ( "businessman" ,"imei",)
    list_display = ('businessman', 'imei','register_date')

admin.site.register(Device,DeviceAdmin)
