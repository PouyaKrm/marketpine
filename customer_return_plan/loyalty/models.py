from django.db import models

from customer_return_plan.models import BaseDiscountSettings
# Create your models here.
from users.models import BaseModel, BusinessmanOneToOneBaseModel, BusinessmanManyToOneBaseModel


class CustomerPurchaseNumberDiscountSettings(BaseModel, BaseDiscountSettings):
    purchase_number = models.PositiveIntegerField(default=0)


class CustomerPurchaseAmountDiscountSettings(BaseModel, BaseDiscountSettings):
    purchase_amount = models.PositiveIntegerField(default=0)


class CustomerLoyaltyDiscountSettings(BaseDiscountSettings, BusinessmanManyToOneBaseModel):
    point = models.PositiveIntegerField(default=0)
    discount_code = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'loyalty_settings'
