from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Businessman, Customer, VerificationCodes


admin.site.register(Businessman, UserAdmin)


class VerificationCodeAdminModel(admin.ModelAdmin):

    list_display = ['code', 'businessman', 'expiration_time']


admin.site.register(VerificationCodes, VerificationCodeAdminModel)

class CustomerAdmin(admin.ModelAdmin):
    exclude = ['last_login']
    list_display = ['phone', 'telegram_id', 'instagram_id', 'register_date', 'businessman']
    ordering = ['first_name', 'last_name']


admin.site.register(Customer, CustomerAdmin)


