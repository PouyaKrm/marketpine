from django.db import models

from customer_return_plan.models import BaseDiscountSettings, Discount
# Create your models here.
from users.models import BaseModel, BusinessmanOneToOneBaseModel, BusinessmanManyToOneBaseModel, Businessman, Customer, \
    BusinessmanCustomer


class CustomerPurchaseNumberDiscountSettings(BaseModel, BaseDiscountSettings):
    purchase_number = models.PositiveIntegerField(default=0)


class CustomerPurchaseAmountDiscountSettings(BaseModel, BaseDiscountSettings):
    purchase_amount = models.PositiveIntegerField(default=0)


class CustomerLoyaltySettings(BusinessmanOneToOneBaseModel):
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'loyalty_settings'


class CustomerLoyaltyDiscountSettings(BaseDiscountSettings, BusinessmanManyToOneBaseModel):
    point = models.PositiveIntegerField(default=0)
    discount_code = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'loyalty_discount_settings'


class CustomerPoints(BusinessmanManyToOneBaseModel):
    customer = models.ForeignKey(Customer, related_name='points', related_query_name='points', on_delete=models.PROTECT)
    point = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'customer_points'
        unique_together = ('businessman', 'customer')
        verbose_name = 'Customer points'
        verbose_name_plural = 'Customer points'


class CustomerExclusiveDiscount(BaseModel):
    businessman_customer = models.ForeignKey(BusinessmanCustomer, on_delete=models.PROTECT,
                                             related_name='exclusive_discounts',
                                             related_query_name='exclusive_discounts',
                                             null=True)
    discount = models.ForeignKey(Discount, on_delete=models.PROTECT, related_name='exclusive_customers',
                                 related_query_name='exclusive_customers',
                                 null=True)

    class Meta:
        db_table = 'customer_exclusive_discounts'
