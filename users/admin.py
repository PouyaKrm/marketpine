from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Salesman, Customer, SalesmenCustomer, VerificationCodes


admin.site.register(Salesman, UserAdmin)
admin.site.register(VerificationCodes)

class CustomerAdmin(admin.ModelAdmin):
    exclude = ['last_login']
    list_display = ['phone', 'first_name', 'last_name', 'email']
    ordering = ['first_name', 'last_name']


admin.site.register(Customer, CustomerAdmin)


admin.site.register(SalesmenCustomer)