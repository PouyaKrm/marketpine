from django.contrib import admin
from .models import Festival
from .forms import FestivalForm
# Register your models here.


class FestivalAdminModel(admin.ModelAdmin):

    list_display = ['name', 'businessman', 'start_date', 'end_date']
    form = FestivalForm


admin.site.register(Festival, FestivalAdminModel)
