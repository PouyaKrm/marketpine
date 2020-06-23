from django.db import models

# Create your models here.
from customerpurchase.models import CustomerPurchase
from users.models import BusinessmanManyToOneBaseModel, Customer, BaseModel


class BaseDiscountSettings(models.Model):
    DISCOUNT_TYPE_PERCENT = '0'
    DISCOUNT_TYPE_FLAT_RATE = '1'

    discount_type_choices = [
        (DISCOUNT_TYPE_PERCENT, 'Percent'),
        (DISCOUNT_TYPE_FLAT_RATE, 'Flat rate')
    ]
    discount_type = models.CharField(max_length=2, null=True, choices=discount_type_choices,
                                     default=DISCOUNT_TYPE_PERCENT)
    percent_off = models.FloatField(default=0)
    flat_rate_off = models.PositiveIntegerField(default=0)

    def is_percent_discount(self) -> bool:
        return self.discount_type == self.DISCOUNT_TYPE_PERCENT

    def is_flat_discount(self) -> bool:
        return self.discount_type == self.DISCOUNT_TYPE_FLAT_RATE


    class Meta:
        abstract = True


class Discount(BusinessmanManyToOneBaseModel, BaseDiscountSettings):

    USED_FOR_NONE = '0'
    USED_FOR_FESTIVAL = '1'
    USED_FOR_INVITATION = '2'
    USED_FOR_LOYALTY_AMOUNT = '3'
    USED_FOR_LOYALTY_NUMBER = '4'

    used_for_choices = [
        (USED_FOR_NONE, 'None'),
        (USED_FOR_FESTIVAL, 'Festival'),
        (USED_FOR_INVITATION, 'Invitation'),
        (USED_FOR_LOYALTY_AMOUNT, 'Loyalty Amount'),
        (USED_FOR_LOYALTY_NUMBER, 'Loyalty Number')
    ]

    discount_code = models.CharField(max_length=20)
    expires = models.BooleanField(default=False)
    expire_date = models.DateTimeField(null=True, blank=True)
    # customers_used = models.ManyToManyField(Customer, related_name="customers_used")
    # purchases = models.ManyToManyField(CustomerPurchase, related_name='purchases', related_query_name='purchases',
    #                                    null=True, blank=True)
    connected_purchases = models.ManyToManyField(CustomerPurchase, through="PurchaseDiscount",
                                                 related_name="connected_purchases",
                                                 related_query_name="connected_purchases")
    used_for = models.CharField(max_length=2, choices=used_for_choices, default=USED_FOR_NONE)
    # reserved_for = models.OneToOneField(Customer, on_delete=models.PROTECT, null=True)

    def set_discount_data(self, discount_code: str, discount_type: str, percent_off: float, flat_rate_off: int):
        if discount_type != Discount.DISCOUNT_TYPE_FLAT_RATE and discount_type != Discount.DISCOUNT_TYPE_PERCENT:
            raise ValueError('invalid value for discount_type')
        self.discount_type = discount_type
        self.percent_off = percent_off
        self.flat_rate_off = flat_rate_off
        self.discount_code = discount_code.lower()

    def set_expire_date_if_expires(self, expires: bool, expire_date):
        self.expires = expires
        if self.expires:
            self.expire_date = expire_date
        else:
            self.expire_date = None

    def amount_of_discount_for_customer(self, customer: Customer):
        amount = self.connected_purchases.filter(customer=customer).first().amount
        if self.is_percent_discount():
            return amount * (self.percent_off / 100)
        return self.flat_rate_off

    def is_festival_discount(self) -> bool:
        return self.used_for == Discount.USED_FOR_FESTIVAL

    def is_invitation_discount(self) -> bool:
        return self.used_for == Discount.USED_FOR_INVITATION


class PurchaseDiscount(BaseModel):

    purchase = models.ForeignKey(CustomerPurchase, on_delete=models.CASCADE, related_name="purchase_discount",
                                 related_query_name="purchase_discount")
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name="purchase_discount",
                                 related_query_name="purchase_discount")

    class Meta:
        unique_together = ['purchase', 'discount']
