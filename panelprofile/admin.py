from wsgiref.util import FileWrapper

from django.contrib import admin
from django.core.checks import messages
from django.http.response import HttpResponse
from django.urls import path, reverse, re_path
from django.utils.html import format_html
from common.util.kavenegar_local import APIException

from .models import SMSPanelInfo, AuthDoc, BusinessmanAuthDocs


# Register your models here.

class SMSPanelInfoAdmin(admin.ModelAdmin):

    list_display = ['username', 'status', 'credit']
    readonly_fields = ['api_key']


class AuthDocAdmin(admin.ModelAdmin):

    fields = ['download_link', 'file']
    readonly_fields = ['download_link']

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


class BusinessmanAuthDocsAdmin(admin.ModelAdmin):

    fields = ['businessman_username', 'form_link', 'card_link', 'certificate_link']
    readonly_fields = ['businessman_username', 'form_link', 'card_link', 'certificate_link']
    actions = ['delete_docs']

    def get_actions(self, request):

        """
        Removes default delete action
        :param request:
        :return:
        """

        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_docs(self, request, queryset):

        """
        An action that deletes selected records using overrided delete method in BusinessmanAuthDocs model
        :param request:
        :param queryset: contains selected BusinessmanAuthDocs records
        :return:
        """

        for obj in queryset.all():
            try:
                obj.delete()
            except APIException as e:
                self.message_user(e.message, request, level=messages.ERROR)
        self.message_user(message='auth docs deleted successfuly', request=request)

    delete_docs.short_description = 'Delete selected records'

    def get_urls(self):

        """
        adds download link for form, national card and birth certificate that is uploaded by the user
        :return: extended urls
        """

        urls = super().get_urls()
        custom_urls = [
            path('download/<int:auth_id>/form/', self.admin_site.admin_view(self.download_form),
                    name='download_form'),
            path('download/<int:auth_id>/card/', self.admin_site.admin_view(self.download_card),
                    name='download_card'),
            path('download/<int:auth_id>/certificate/', self.admin_site.admin_view(self.download_certificate),
                    name='download_certificate')
        ]

        return custom_urls + urls


    def form_link(self, obj):
        """
        generates download link for form
        :param obj: BusinessmanAuthDocs
        :return: form download link
        """
        return self.get_download_link(obj, 'form')

    form_link.short_description = 'uploaded form'
    form_link.allow_tags = True

    def card_link(self, obj):

        """
        generates download link for uploaded the national card
        :param obj: BusinessmanAuthDocs
        :return: national card download link
        """

        return self.get_download_link(obj, 'card')

    card_link.short_description = 'uploaded card'
    card_link.allow_tags = True

    def certificate_link(self, obj):

        """
        generates download link for the uploaded birth certificate
        :param obj: BusinessmanAuthDocs
        :return: birth certificate download link
        """

        return self.get_download_link(obj, 'certificate')

    certificate_link.short_description = 'uploaded certificate'
    certificate_link.allow_tags = True



    def get_download_link(self, obj, file_type):

        """
        download link generation is handled by this function and based on the file type
        :param obj: BusinessmanAuthDocs
        :param file_type: possible values are 'form', 'card', 'certificate'
        :return: download link if valid file_type is presented, else a simple text message will be returned
        """

        if obj.pk is None:
            return "no file exists"

        if file_type == 'form' and obj.form.name:
            return format_html("<a href='{}' target='_blank'>{}</a>",
                               reverse('admin:download_form', args=[obj.pk]), obj.form.name)
        elif file_type == 'card' and obj.national_card.name:
            return format_html("<a href='{}' target='_blank'>{}</a>",
                               reverse('admin:download_card', args=[obj.pk]), obj.national_card.name)
        elif file_type == 'certificate' and obj.birth_certificate.name:
            return format_html("<a href='{}' target='_blank'>{}</a>",
                               reverse('admin:download_certificate', args=[obj.pk]), obj.birth_certificate.name)
        else:
            return file_type + ' is not uploaded yet'

    def download_files(self, request, auth_id, file_type):

        """
        Providing uploaded file is handled by this function and return file bytes based on provided  file_type
        parameter
        :param request:
        :param auth_id: id of the selected BusinessmanAuthDocs record to fetch it files
        :param file_type: possible values are 'form', 'card' and 'certificate' for other values 'form' is selected
        :return: returns HttpResponse with body that contains file binary data
        """

        qs = BusinessmanAuthDocs.objects.get(pk=auth_id)
        type = 'image/png'
        if file_type == 'form':
            file = qs.form.file
            type = 'application/pdf'
        elif file_type == 'card':
            file = qs.national_card.file

        elif file_type == 'certificate':
            file = qs.birth_certificate.file
        else:
            file = qs.form.file

        return HttpResponse(FileWrapper(file), content_type=type)

    def download_form(self, request, auth_id):
        return self.download_files(request, auth_id, 'form')

    def download_card(self, request, auth_id):
        return self.download_files(request, auth_id, 'card')

    def download_certificate(self, request, auth_id):
        return self.download_files(request, auth_id, 'certificate')


admin.site.register(BusinessmanAuthDocs, BusinessmanAuthDocsAdmin)
