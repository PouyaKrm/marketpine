from django.db import models

# Create your models here.
from users.models import BusinessmanManyToOneBaseModel, Customer


class BaseInvitationDiscountSettings(models.Model):
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

    class Meta:
        abstract = True


class Discount(BusinessmanManyToOneBaseModel, BaseInvitationDiscountSettings):

    discount_code = models.CharField(max_length=20)
    expires = models.BooleanField(default=False)
    expire_date = models.DateTimeField(null=True, blank=True)
    customers_used = models.ManyToManyField(Customer, related_name="customers_used")

    def set_discount_data(self, discount_code: str, discount_type: str, percent_off: float, flat_rate_off: int):
        if discount_type != Discount.DISCOUNT_TYPE_FLAT_RATE and discount_type != Discount.DISCOUNT_TYPE_PERCENT:
            raise ValueError('invalid value for discount_type')
        self.discount_type = discount_type
        self.percent_off = percent_off
        self.flat_rate_off = flat_rate_off
        self.discount_code = discount_code

    def set_expire_date_if_expires(self, expires: bool, expire_date):
        self.expires = expires
        if self.expires:
            self.expire_date = expire_date
        else:
            self.expire_date = None
