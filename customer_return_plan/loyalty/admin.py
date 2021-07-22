from django.contrib import admin

from .forms import CustomerLoyaltyAdminForm
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseNumberDiscountSettings,
                     CustomerPurchaseAmountDiscountSettings, CustomerPoints)


class CustomerLoyaltyAdminModel(admin.ModelAdmin):
    form = CustomerLoyaltyAdminForm
    list_display = ['businessman', 'create_date', 'point', 'discount_type', 'discount_value_by_discount_type']


class CustomerPointsAdminModel(admin.ModelAdmin):
    list_display = ['businessman', 'customer', 'point']


admin.site.register(CustomerLoyaltyDiscountSettings, CustomerLoyaltyAdminModel)
admin.site.register(CustomerPoints, CustomerPointsAdminModel)
admin.site.register(CustomerPurchaseAmountDiscountSettings)
admin.site.register(CustomerPurchaseNumberDiscountSettings)
