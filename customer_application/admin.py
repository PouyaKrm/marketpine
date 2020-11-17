from django.contrib import admin

# Register your models here.

from .models import CustomerVerificationCode, CustomerLoginTokens

admin.site.register(CustomerVerificationCode)
admin.site.register(CustomerLoginTokens)
