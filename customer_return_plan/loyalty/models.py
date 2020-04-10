from django.db import models
from customer_return_plan.models import BaseDiscountSettings

# Create your models here.
from users.models import BaseModel, BusinessmanOneToOneBaseModel


class CustomerPurchaseNumberDiscountSettings(BaseModel, BaseDiscountSettings):
    purchase_number = models.PositiveIntegerField(default=0)


class CustomerPurchaseAmountDiscountSettings(BaseModel, BaseDiscountSettings):
    purchase_amount = models.PositiveIntegerField(default=0)


class CustomerLoyaltyDiscountSettings(BusinessmanOneToOneBaseModel):

    FOR_PURCHASE_AMOUNT = '0'
    FOR_PURCHASE_NUMBER = '1'
    FOR_BOTH = '2'

    use_choices = [
        (FOR_PURCHASE_AMOUNT, 'Purchase Amount'),
        (FOR_PURCHASE_NUMBER, 'Purchase Number'),
        (FOR_BOTH, 'Both')
    ]

    purchase_number_settings = models.OneToOneField(CustomerPurchaseNumberDiscountSettings, on_delete=models.CASCADE)
    purchase_amount_settings = models.OneToOneField(CustomerPurchaseAmountDiscountSettings, on_delete=models.CASCADE)
    create_discount_for = models.CharField(max_length=2, choices=use_choices, default=FOR_BOTH)
    disabled = models.BooleanField(default=False)

    def is_discount_for_purchase_amount(self) -> bool:
        return self.create_discount_for == CustomerLoyaltyDiscountSettings.FOR_PURCHASE_AMOUNT

    def is_discount_for_purchase_number(self) -> bool:
        return self.create_discount_for == CustomerLoyaltyDiscountSettings.FOR_PURCHASE_NUMBER

    def is_discount_for_both(self) -> bool:
        return self.create_discount_for == CustomerLoyaltyDiscountSettings.FOR_BOTH
