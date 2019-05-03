from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Businessman, Customer, VerificationCodes


admin.site.register(Businessman, UserAdmin)
admin.site.register(VerificationCodes)

class CustomerAdmin(admin.ModelAdmin):
    exclude = ['last_login']
    list_display = ['phone', 'telegram_id', 'instagram_id', 'register_date', 'businessman']
    ordering = ['first_name', 'last_name']


admin.site.register(Customer, CustomerAdmin)


