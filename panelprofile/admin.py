from wsgiref.util import FileWrapper

from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import SMSPanelInfo, AuthDoc

# Register your models here.

class SMSPanelInfoAdmin(admin.ModelAdmin):

    list_display = ['username', 'status', 'credit']



class AuthDocAdmin(admin.ModelAdmin):

    fields = ['download_link', 'file']
    readonly_fields = ['download_link']
    # list_display = ['download_link']

    def get_urls(self):
        urls = super().get_urls()
        custom_url = [
            path('download/<int:file_id>/', self.admin_site.admin_view(self.download_file), name='download')

        ]

        return custom_url + urls

    def download_link(self, obj):
        if obj.pk is not None:
            return format_html("<a href='{}' target='_blank'>{}</a>", reverse('admin:download', args=[obj.pk]), obj.file.name)
        return "no file exist"
    download_link.short_description = 'download file'
    download_link.allow_tags = True

    def download_file(self, request, file_id):

        qs = AuthDoc.objects.get(pk=file_id)
        return HttpResponse(FileWrapper(qs.file), content_type='application/pdf')


admin.site.register(SMSPanelInfo, SMSPanelInfoAdmin)

admin.site.register(AuthDoc, AuthDocAdmin)
