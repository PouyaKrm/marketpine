from django.contrib import admin

from .models import Discount, PurchaseDiscount

admin.site.register(Discount)
admin.site.register(PurchaseDiscount)
