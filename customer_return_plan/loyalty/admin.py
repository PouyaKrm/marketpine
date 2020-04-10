from django.contrib import admin
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseNumberDiscountSettings,
                     CustomerPurchaseAmountDiscountSettings)

# Register your models here.
admin.site.register(CustomerLoyaltyDiscountSettings)
admin.site.register(CustomerPurchaseAmountDiscountSettings)
admin.site.register(CustomerPurchaseNumberDiscountSettings)
