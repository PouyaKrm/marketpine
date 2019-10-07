from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.checks import messages
from django.db.models import QuerySet
from django.http.request import HttpRequest
from kavenegar import APIException

from common.util.sms_panel import ClientManagement
from .models import Businessman, Customer, VerificationCodes
from . import forms


class BusinessmanAdminModel(UserAdmin):
    add_form = forms.BusinessmanCreationFrom
    form = forms.BusinessmanChangeForm
    model = Businessman
    list_display = ['id', 'username', 'business_name', 'phone', 'authorized']
    actions = ['authorize_pending_users', 'un_authorize_users']
    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('General Info', {'fields': ('business_name', 'phone', 'logo', 'address', 'email')}),
            ('Permissions', {'fields': ('is_verified', 'authorized')}),
                 )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('General Info', {'fields': ('business_name', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_verified', 'authorized')}),
        )

    def authorize_pending_users(self, request, queryset):
        """
        an action that sets user's sms panel status to active with login in kavenegar. this action will not be executed
        for is_staff members
        :param request:
        :param queryset: users objects that is selected by admin
        :return:
        """

        client_manage = ClientManagement()
        for obj in queryset.all():
            if obj.authorized == '1' and obj.is_staff is False:
                try:
                    resp = client_manage.activate_sms_panel(obj.smspanelinfo.api_key)
                    obj.smspanelinfo.status = '1'
                    obj.authorized = '2'
                    obj.save()
                except APIException as e:
                    self.message_user(request, f'error {e.status} in user {obj.username} authorization with message: {e.message}'
                                      , messages.ERROR)

        self.message_user(request, 'all users authorized successfully')
    authorize_pending_users.short_description = 'authorize pending users'


    def un_authorize_users(self, request, queryset):

        """
        un authorizes users adn deactivate their sms panel
        :param request:
        :param queryset: users that are selected by the admin
        :return:
        """

        client_manage = ClientManagement()
        for obj in queryset.all():
            if obj.authorized != '0' and obj.is_staff is False:

                try:
                    client_manage.deactivate_sms_panel(obj.smspanelinfo.api_key)
                    obj.smspanelinfo.status = '0'
                    obj.authorized = '0'
                    obj.save()
                except APIException as e:
                    self.message_user(request, f'error {e.status} in user {obj.username} authorization with message: {e.message}'
                                      , messages.ERROR)

        self.message_user(request, 'all users un authorized successfully')

    un_authorize_users.short_description = 'un authorize users'





admin.site.register(Businessman, BusinessmanAdminModel)


class VerificationCodeAdminModel(admin.ModelAdmin):

    list_display = ['code', 'businessman', 'expiration_time']


admin.site.register(VerificationCodes, VerificationCodeAdminModel)


class CustomerAdmin(admin.ModelAdmin):
    exclude = ['last_login']
    list_display = ['phone', 'full_name', 'register_date', 'businessman']


admin.site.register(Customer, CustomerAdmin)


