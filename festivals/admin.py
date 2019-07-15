from django.contrib import admin
from .models import Festival
# Register your models here.


class FestivalAdminModel(admin.ModelAdmin):

    list_display = ['name', 'businessman', 'start_date', 'end_date']


admin.site.register(Festival, FestivalAdminModel)
