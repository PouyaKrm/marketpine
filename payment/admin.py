from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    fields = ( "businessman" ,"authority" ,"refid" ,
    "create_status" ,"description" ,"phone" ,"amount")
    list_display = ('businessman', 'payment_type', 'create_status', 'verification_status', 'creation_date', 'authority', 'refid')
    list_filter = ('create_status', 'businessman')

admin.site.register(Payment,PaymentAdmin)
