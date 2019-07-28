from django.db import models

# Create your models here.
from users.models import Customer, Businessman


class CustomerPurchase(models.Model):

    amount = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    class Meta:

        db_table = 'customer_purchases'


