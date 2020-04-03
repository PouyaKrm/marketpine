from django.db import models

# Create your models here.
from users.models import Customer, Businessman, BusinessmanManyToOneBaseModel


class CustomerPurchase(BusinessmanManyToOneBaseModel):

    amount = models.PositiveIntegerField()
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)

    class Meta:

        db_table = 'customer_purchases'


