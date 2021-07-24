from django.contrib import admin

from .forms import CustomerLoyaltyDiscountSettingsAdminForm, CustomerLoyaltySettingsForm
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseNumberDiscountSettings,
                     CustomerPurchaseAmountDiscountSettings, CustomerPoints, CustomerLoyaltySettings)


class CustomerLoyaltySettingsAdminModel(admin.ModelAdmin):
    form = CustomerLoyaltySettingsForm
    list_display = ['businessman', 'is_active', 'create_date', 'update_date']


class CustomerLoyaltyDiscountSettingAdminModel(admin.ModelAdmin):
    form = CustomerLoyaltyDiscountSettingsAdminForm
    list_display = ['loyalty_settings', 'create_date', 'point', 'discount_type', 'discount_value_by_discount_type']


class CustomerPointsAdminModel(admin.ModelAdmin):
    list_display = ['businessman', 'customer', 'point']


admin.site.register(CustomerLoyaltySettings, CustomerLoyaltySettingsAdminModel)
admin.site.register(CustomerLoyaltyDiscountSettings, CustomerLoyaltyDiscountSettingAdminModel)
admin.site.register(CustomerPoints, CustomerPointsAdminModel)
admin.site.register(CustomerPurchaseAmountDiscountSettings)
admin.site.register(CustomerPurchaseNumberDiscountSettings)
