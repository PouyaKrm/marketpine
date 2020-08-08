from django.contrib import admin

# Register your models here.

from .models import CustomerOneTimePasswords, CustomerLoginTokens

admin.site.register(CustomerOneTimePasswords)
admin.site.register(CustomerLoginTokens)
