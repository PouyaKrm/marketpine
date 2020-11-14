from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.checks import messages
from django.shortcuts import redirect, render
from django.urls import reverse, path
from django.utils.html import format_html
from kavenegar import APIException
from .models import Businessman, Customer, VerificationCodes, AuthStatus, BusinessCategory, \
    BusinessmanCustomer
from . import forms


def generate_button_link(disable: bool, button_color='blue'):
    if disable is False:
        return '<a href={} ' \
               'style="background:  ' + button_color + \
               ';color: white; padding: 6px; border: 0; margin: 2px 0; border-radius: 6px">{}</a>'

    return 'this user is not in pending mode'


class BusinessmanAdminModel(UserAdmin):
    add_form = forms.BusinessmanCreationFrom
    form = forms.BusinessmanChangeForm
    model = Businessman
    list_display = ['id', 'username', 'business_name', 'phone', 'authorized', 'get_authorize_link',
                    'get_un_authorize_link']
    readonly_fields = ['authorized']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('General Info', {'fields': ('page_id', 'business_name', 'phone', 'logo', 'address', 'email', 'business_category')}),
        ('Permissions', {
            'fields': [
                'is_verified', 'authorized', 'has_sms_panel', 'panel_activation_date', 'panel_expiration_date',
                'duration_type'
            ]}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('General Info', {'fields': ('page_id', 'business_name', 'business_category', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_verified', 'panel_activation_date', 'panel_expiration_date',
                'duration_type')}),
    )

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path('authorize-user/<int:user_id>/', self.admin_site.admin_view(self.authorize_user), name='authorize'),
            path('un-authorize-user/<int:user_id>/', self.admin_site.admin_view(self.un_authorize_user),
                 name='un_authorize')
        ]

        return custom_urls + urls

    def get_authorize_link(self, obj):

        """
        generates authorization link in django admin
        :param obj: Businessman
        :return: HTML code of the link
        """
        return format_html(generate_button_link(obj.authorized != AuthStatus.PENDING),
                           reverse('admin:authorize', args=[obj.pk]), 'Authorize')

    get_authorize_link.short_description = 'Authorize user'

    def authorize_user(self, request, user_id):

        """
        user authorization is handled by this function
        :param request:
        :param user_id: id of the businessman
        :return: if request method is 'GET' return template of authorization link
        else if method is 'POST' will authorize the user and redirects user to changelist page
        """

        if request.method == 'GET':
            return render(request, '../templates/users/authorize_user.html',
                          {'businessman': Businessman.objects.get(pk=user_id)})

        if request.method != 'POST':
            return redirect(reverse('admin:users_businessman_changelist'))

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

        return format_html(generate_button_link(False, 'red'), reverse('admin:un_authorize', args=[obj.pk]),
                           'UnAuthorize')

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
            return render(request, '../templates/users/un_authorize_user.html', {'businessman': businessman})

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
    list_display = ['phone', 'id', 'full_name', 'register_date']


admin.site.register(Customer, CustomerAdmin)


class BusinessCategoryAdminModel(admin.ModelAdmin):
    list_display = ['name', 'create_date', 'update_date']


admin.site.register(BusinessCategory, BusinessCategoryAdminModel)


class BusinessmanCustomerAdminModel(admin.ModelAdmin):
    list_display = ['businessman', 'customer', 'businessman_id', 'customer_id', 'joined_by']


admin.site.register(BusinessmanCustomer, BusinessmanCustomerAdminModel)
