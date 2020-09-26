from django.contrib import admin

from .forms import EducationCreationForm
from .models import Education, EducationType

# Register your models here.


class EducationTypeAdminModel(admin.ModelAdmin):

    list_display = ['name', 'id', 'create_date', 'update_date']



class EducationAdminModel(admin.ModelAdmin):

    list_display = ['title', 'create_date', 'update_date']
    form = EducationCreationForm


admin.site.register(EducationType, EducationTypeAdminModel)
admin.site.register(Education, EducationAdminModel)
