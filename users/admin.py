from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.checks import messages
from django.shortcuts import redirect, render
from django.urls import reverse, path
from django.utils.html import format_html
from kavenegar import APIException

from common.util.sms_panel import ClientManagement
from panelprofile.models import SMSPanelStatus
from .models import Businessman, Customer, VerificationCodes, AuthStatus
from . import forms


def generate_button_link(disable: bool):

    if disable is False:
        return '<a href={} target="_blank" ' \
               'style="background: blue; color: white; padding: 6px; border: 0; margin: 2px 0; border-radius: 6px">{}</a>'

    return 'this user is not in pending mode'


class BusinessmanAdminModel(UserAdmin):

    add_form = forms.BusinessmanCreationFrom
    form = forms.BusinessmanChangeForm
    model = Businessman
    list_display = ['id', 'username', 'business_name', 'phone', 'authorized', 'get_authorize_link', 'get_un_authorize_link']
    readonly_fields = ['authorized']
    actions = ['authorize_pending_users', 'un_authorize_users']
    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('General Info', {'fields': ('business_name', 'phone', 'logo', 'address', 'email')}),
            ('Permissions', {'fields': ['is_verified', 'authorized']}),
                 )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('General Info', {'fields': ('business_name', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_verified',)}),
        )

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path('authorize-user/<int:user_id>/', self.admin_site.admin_view(self.authorize_user), name='authorize'),
            path('un-authorize-user/<int:user_id>/', self.admin_site.admin_view(self.un_authorize_user), name='un_authorize')
        ]

        return custom_urls + urls

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
                    obj.smspanelinfo.status = SMSPanelStatus.ACTIVE_LOGIN
                    obj.authorized = AuthStatus.AUTHORIZED
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
            if obj.authorized != AuthStatus.UNAUTHORIZED and obj.is_staff is False:

                try:
                    client_manage.deactivate_sms_panel(obj.smspanelinfo.api_key)
                    obj.smspanelinfo.status = SMSPanelStatus.INACTIVE
                    obj.authorized = AuthStatus.UNAUTHORIZED
                    obj.save()
                except APIException as e:
                    self.message_user(request, f'error {e.status} in user {obj.username} authorization with message: {e.message}'
                                      , messages.ERROR)

        self.message_user(request, 'all users un authorized successfully')

    un_authorize_users.short_description = 'un authorize users'


    def get_authorize_link(self, obj):

        """
        generates authorization link in django admin
        :param obj: Businessman
        :return: HTML code of the link
        """
        return format_html(generate_button_link(obj.authorized != AuthStatus.PENDING),
                           reverse('admin:authorize', args=[obj.pk]), 'Authorize')

    get_authorize_link.short_description = 'Authorize user'


    def authorize_user(self, request,  user_id):

        """
        user authorization is handled by this function
        :param request:
        :param user_id: id of the businessman
        :return: if request method is 'GET' return template of authorization link
        else if method is 'POST' will authorize the user and redirects user to changelist page
        """

        if request.method == 'GET':
            return render(request, '../templates/users/authorize_user.html', {'businessman': Businessman.objects.get(pk=user_id)})


        if request.method != 'POST':
            return

        businessman = Businessman.objects.get(pk=user_id)

        if hasattr(businessman, 'businessmanauthdocs') is False:
            self.message_user(request, 'user does not have businessmanauthdocs', level=messages.ERROR)
            return redirect(reverse('admin:users_businessman_changelist'))

        if businessman.authorized == AuthStatus.PENDING:
            try:
                businessman.businessmanauthdocs.authorize_user()
            except APIException as e:
                self.message_user(request, e.message, level=messages.ERROR)

        return redirect(reverse('admin:users_businessman_changelist'))


    def get_un_authorize_link(self, obj):

        """
        generates unauthorization link in django admin
        :param obj: Businessman
        :return: HTML code of the unauthorization link
        """

        return format_html(generate_button_link(False), reverse('admin:un_authorize', args=[obj.pk]), 'UnAuthorize')

    get_un_authorize_link.short_description = 'un authorize user'

    def un_authorize_user(self, request, user_id):

        """
        user unauthorization is handled by this function.
        :param request:
        :param user_id: id of the businessman
        :return: If request mehtod is 'GET' returns template of unauthorization page
        else If request method is 'POST' will unauthorizes user and redirects to changelist page
        """

        businessman = Businessman.objects.get(pk=user_id)

        if request.method == 'GET':
            return render(request, '../templates/users/un_authorize_user.html',
                          {'businessman': businessman})

        if request.method != 'POST' or businessman.authorized == AuthStatus.UNAUTHORIZED:
            return redirect(reverse('admin:users_businessman_changelist'))

        businessman.businessmanauthdocs.un_authorize_user()

        return redirect(reverse('admin:users_businessman_changelist'))


admin.site.register(Businessman, BusinessmanAdminModel)


class VerificationCodeAdminModel(admin.ModelAdmin):

    list_display = ['code', 'businessman', 'expiration_time']


admin.site.register(VerificationCodes, VerificationCodeAdminModel)


class CustomerAdmin(admin.ModelAdmin):
    exclude = ['last_login']
    list_display = ['phone', 'full_name', 'register_date', 'businessman']


admin.site.register(Customer, CustomerAdmin)
