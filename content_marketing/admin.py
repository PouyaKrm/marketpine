from django.contrib import admin
from .models import Video

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title','creation_date','videofile')

admin.site.register(Video,VideoAdmin)
