from django.contrib import admin

from .forms import SubscriptionPlanForm, WalletForm
from .models import Payment, FailedPaymentOperation, SubscriptionPlan, Wallet, Billing


class PaymentAdmin(admin.ModelAdmin):
    fields = ("businessman", "authority", "refid",
              "create_status", "description", "phone", "amount", 'panel_plan', 'call_back_status')
    list_display = (
        'businessman', 'payment_type', 'create_status', 'verification_status', 'creation_date', 'authority', 'refid')
    list_filter = ('create_status', 'businessman')


class WalletModelAdmin(admin.ModelAdmin):
    list_display = ['businessman', 'available_credit', 'used_credit', 'last_credit_increase_date', 'create_date']
    list_display_links = ['businessman', 'available_credit', 'used_credit', 'last_credit_increase_date', 'create_date']
    form = WalletForm


class BillingModelAdmin(admin.ModelAdmin):
    list_display = ['businessman', 'amount', 'customer_added', 'create_date']
    list_display_links = ['businessman', 'amount', 'customer_added', 'create_date']


class PaymentOperationFailedAdmin(admin.ModelAdmin):
    list_display = ('businessman', 'operation_type', 'create_date', 'payment_amount', 'is_fixed')


class SubscriptionPlanModelAdmin(admin.ModelAdmin):
    list_display = ['price_in_toman', 'title', 'duration']
    form = SubscriptionPlanForm


admin.site.register(Payment, PaymentAdmin)
admin.site.register(FailedPaymentOperation, PaymentOperationFailedAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanModelAdmin)
admin.site.register(Wallet, WalletModelAdmin)
admin.site.register(Billing, BillingModelAdmin)
