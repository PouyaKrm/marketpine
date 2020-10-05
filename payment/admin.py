from django.contrib import admin
from .models import Payment, FailedPaymentOperation, PanelActivationPlans


class PaymentAdmin(admin.ModelAdmin):
    fields = ( "businessman" ,"authority" ,"refid" ,
    "create_status" ,"description" ,"phone" ,"amount")
    list_display = ('businessman', 'payment_type', 'create_status', 'verification_status', 'creation_date', 'authority', 'refid')
    list_filter = ('create_status', 'businessman')


class PaymentOperationFailedAdmin(admin.ModelAdmin):
    list_display = ('businessman', 'operation_type', 'create_date', 'payment_amount', 'is_fixed')

class PanelActiovationPalnModelAdmin(admin.ModelAdmin):
    list_display = ['price_in_toman', 'duration_type', 'is_permanent', 'title']
    readonly_fields = ['duration']


admin.site.register(Payment, PaymentAdmin)
admin.site.register(FailedPaymentOperation, PaymentOperationFailedAdmin)
admin.site.register(PanelActivationPlans, PanelActiovationPalnModelAdmin)