from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    fields = ( "businessman" ,"authority" ,"refid" ,
    "status" ,"description" ,"phone" ,"amount")
    list_display = ('businessman', 'status','creation_date', 'authority','refid')
    list_filter =('status', 'businessman')

admin.site.register(Payment,PaymentAdmin)
