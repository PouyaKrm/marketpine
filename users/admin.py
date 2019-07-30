from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Businessman, Customer, VerificationCodes
from . import forms


class BusinessmanAdminModel(UserAdmin):
    add_form = forms.BusinessmanCreationFrom
    form = forms.BusinessmanChangeForm
    model = Businessman
    list_display = ['username', 'business_name', 'phone']
    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('General Info', {'fields': ('business_name', 'phone', 'address')}),
            ('Permissions', {'fields': ('is_verified', 'bot_access_expire',
                                        'instagram_access_expire', 'friend_invitation_access_expire')}),
                 )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('General Info', {'fields': ('business_name', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_verified', 'bot_access_expire',
                                    'instagram_access_expire', 'friend_invitation_access_expire')}),
        )


admin.site.register(Businessman, BusinessmanAdminModel)


class VerificationCodeAdminModel(admin.ModelAdmin):

    list_display = ['code', 'businessman', 'expiration_time']


admin.site.register(VerificationCodes, VerificationCodeAdminModel)


class CustomerAdmin(admin.ModelAdmin):
    exclude = ['last_login']
    list_display = ['phone', 'full_name', 'register_date', 'businessman']

admin.site.register(Customer, CustomerAdmin)


