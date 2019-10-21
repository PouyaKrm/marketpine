from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    fields = ( "businessman" ,"authority" ,"refid" ,
    "status" ,"description" ,"phone" ,"amount")
    list_display = ('businessman', 'status','creation_date', 'authority')

admin.site.register(Payment,PaymentAdmin)
