from django.contrib import admin

from .forms import CustomerLoyaltyAdminForm
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseNumberDiscountSettings,
                     CustomerPurchaseAmountDiscountSettings)


class CustomerLoyaltyAdminModel(admin.ModelAdmin):
    form = CustomerLoyaltyAdminForm
    list_display = ['businessman', 'create_date', 'point', 'discount_type', 'discount_value_by_discount_type']


admin.site.register(CustomerLoyaltyDiscountSettings, CustomerLoyaltyAdminModel)
admin.site.register(CustomerPurchaseAmountDiscountSettings)
admin.site.register(CustomerPurchaseNumberDiscountSettings)
