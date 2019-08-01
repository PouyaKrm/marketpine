from django.contrib import admin
from .models import CustomerPurchase
# Register your models here.


class CustomerPurchaseAdminModel(admin.ModelAdmin):

    list_display = ['amount', 'purchase_date', 'customer_phone']

    def customer_phone(self, obj):
        if obj.customer is not None:
            return obj.customer.phone

        return '-'


admin.site.register(CustomerPurchase, CustomerPurchaseAdminModel)
