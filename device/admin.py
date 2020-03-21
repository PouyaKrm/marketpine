from django.contrib import admin
from .models import Device


class DeviceAdmin(admin.ModelAdmin):
    fields = ( "businessman", "imei", 'key', 'disabled')
    list_display = ('businessman', 'imei', 'create_date', 'disabled')
    readonly_fields = ['key']


admin.site.register(Device, DeviceAdmin)
