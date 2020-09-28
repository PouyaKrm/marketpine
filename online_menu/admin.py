from django.contrib import admin

# Register your models here.
from online_menu.models import OnlineMenu


class OnlineMenuModelAdmin(admin.ModelAdmin):
    list_display = ['businessman', 'show_order', 'image']


admin.site.register(OnlineMenu, OnlineMenuModelAdmin)
